import imaplib
import sys
import os
import email
import ssl
from typing import Dict, Any, Optional, List


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from config.config import IMAP_SERVER, EMAIL_ADDRESS, APP_PASSWORD

def format_email(email_str: str) -> str:
    if '<' in email_str and '>' in email_str:
        try:
            email_id = email_str.split('<')[1].split('>')[0]
            return email_id.strip()
        except IndexError:
            return email_str.strip()
    return email_str.strip()

def get_email_body(msg: email.message.Message) -> str:

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdisp:
                try:
                    payload = part.get_payload(decode=True)
                    return payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
                except Exception:
                    return "[Error: Could not decode message body.]"
    else:
        try:
            return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='replace')
        except Exception:
            return "[Error: Could not decode message body.]"

    return "[Body not found or was only HTML/Attachment.]"


def connect_and_read_new_emails() -> Optional[List[Dict[str, str]]]:
    try:
        all_mails = []
        context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, port=993, ssl_context=context)
        mail.login(EMAIL_ADDRESS, APP_PASSWORD)
        mail.select('inbox')

        status, email_ids = mail.search(None, 'UNSEEN')
        id_list: List[bytes] = email_ids[0].split()

        if not id_list:
            print("No new (UNSEEN) emails found.")
            mail.logout()
            return


        for num in id_list:
            status, data = mail.fetch(num, '(RFC822)')

            if status == 'OK':
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                body_text = get_email_body(msg)

                mail_details = {
                    "mail_id": format_email(msg['From']),
                    "subject": msg['Subject'],
                    "body": body_text
                }

                all_mails.append(mail_details)

                mail.store(num, '+FLAGS', '\Seen')
                mail.logout()
                return all_mails

            else:
                print(f"Error fetching email ID {num.decode()}")

        mail.logout()

    except imaplib.IMAP4.error as e:
        print(f"\n IMAP Error: {e}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")


if __name__ == "__main__":
    x = connect_and_read_new_emails()
    print(x)