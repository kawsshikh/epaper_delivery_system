import sys
import os
import time
import schedule
import threading
from typing import Dict, Any, Optional, List
import re
from dateutil import parser
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.pdf_generator import get_epaper_details
from config.config import (
    date_url,
    epaper_directory_list,
    EPAPER_DIRECTORY,
    epaper_names,
    date_pattern
)
from email_handler.send_email import send_email_with_pdf
from email_handler.read_emails import connect_and_read_new_emails
from db.postgres_curd import get_details, insert_epaper

def standardize_date(date_input: str) -> str:
    try:
        parsed_date = parser.parse(date_input, dayfirst=True)
        standardized_format = parsed_date.strftime("%d-%m-%Y")
        return standardized_format
    except ValueError:
        print("Invalid date format")
        return None

def get_newspaper(epaper_details: Dict[str, str], date: str = date_url) -> Optional[Dict[str, Any]]:
    try:
        url = epaper_details["Epaper_url"].replace("(__holder__)", date)
        print(url)
        epaper_details["Epaper_url"] = url
        date_for_filename = date.replace("/", "-")

        pdf_details = get_epaper_details(epaper_details["epaper_name"], url, date_for_filename)
        return pdf_details
    except Exception as e:
        print(f"Error during PDF generation for {epaper_details.get('epaper_name', 'Unknown')}: {e}")
        return None


def custom_get(newspaper_name: str, date: str, email: str) -> None:
    print(f"\n-> Processing request for {newspaper_name} on {date} for {email}")
    epaper_details = EPAPER_DIRECTORY.get(newspaper_name.lower())

    if epaper_details is None:
        print(f"Error: Newspaper '{newspaper_name}' not found in directory.")
        return

    try:
        epaper_key = epaper_details["epaper_name"]

        check_db = get_details(epaper_key, date)

        if check_db:
            print(f"✅ Found existing PDF for {epaper_key}. Sending...")
            send_email_with_pdf(email, check_db["file_path"])
            return

        print(f"⏳ PDF not found in DB. Scraping and generating for {epaper_key}...")

        date_for_url = date.replace('-', '/')

        pdf_details = get_newspaper(epaper_details, date_for_url)

        if pdf_details:
            insert_epaper(pdf_details["epaper_name"], pdf_details["date"], pdf_details["file_path"])
            send_email_with_pdf(email, pdf_details["file_path"])
            print(f"Successfully generated, inserted, and sent PDF for {epaper_key}.")
        else:
            print(f"Failed to generate PDF for {epaper_key}.")

    except Exception as e:
        print(f"An error occurred while fulfilling request for {newspaper_name}: {e}")


def email_listener() -> None:
    POLLING_INTERVAL = 30

    while True:
        try:
            print(f"\n[EMAIL LISTENER] Checking for new mail at {time.strftime('%H:%M:%S')}...")
            emails = connect_and_read_new_emails()

            if emails:
                for mail_data in emails:
                    subject = mail_data["subject"]
                    body = mail_data["body"]

                    if "epaper" in subject.lower():
                        epaper_match = re.search(epaper_names, body, re.IGNORECASE)
                        date_match = re.search(date_pattern, body, re.IGNORECASE)

                        if epaper_match and date_match:
                            epaper_name = epaper_match.group(0)
                            date = standardize_date(date_match.group(0))
                            recipient_email = mail_data["mail_id"]

                            print(f"Found request: {epaper_name} on {date} from {recipient_email}")
                            custom_get(epaper_name, date, recipient_email)
                        else:
                            print(f"Mail subject matched 'epaper' but could not parse name/date in body.")

        except Exception as e:
            print(f" Error during email check cycle: {e}")

        time.sleep(POLLING_INTERVAL)


def run_daily_scraper() -> None:
    print("\n" + "=" * 40)
    print("STARTING DAILY EPAPER GATHERING ")
    print("=" * 40)
    for epaper in epaper_directory_list:
        try:
            details = get_newspaper(epaper)
            if details:
                insert_epaper(details["epaper_name"], details["date"], details["file_path"])
                print(f"Daily job complete for {details['epaper_name']}.")
            else:
                print(f"Daily job failed for {epaper.get('epaper_name', 'Unknown')}.")
        except Exception as e:
            print(f" Unhandled error in daily job for {epaper.get('epaper_name', 'Unknown')}: {e}")


def daily_scheduler() -> None:
    schedule_time = "18:10"
    print(f"Setting up daily scrape job for {schedule_time}")
    schedule.every().day.at(schedule_time).do(run_daily_scraper)

    while True:
        schedule.run_pending()
        time.sleep(1)


def process() -> None:
    print(" Starting E-paper Delivery System...")

    email_thread = threading.Thread(target=email_listener, daemon=True)
    email_thread.start()

    daily_thread = threading.Thread(target=daily_scheduler, daemon=True)
    daily_thread.start()

    try:
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\nMain application exit requested.")
    finally:
        print(" Shutting down E-paper services.")


if __name__ == "__main__":
    process()