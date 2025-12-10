from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

utc_530 = timezone(timedelta(hours=5, minutes=30))
date_url = datetime.now(utc_530).strftime("%d/%m/%Y")
date_pattern = r"(\b\d{1,4}[-/\\.]\d{1,2}[-/\\.]\d{2,4}\b|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s*\d{4}\b)"
epaper_names = r"(eenadu|sakshi|andhrajyothy|all)"

IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("APP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


epaper_directory_list = [
    {
        "epaper_name": "eenadu",
        "Epaper_url": "https://epaper.eenadu.net/Home/Index?date=(__holder__)&eid=2"
    },
    {
        "epaper_name": "sakshi",
        "Epaper_url": "https://epaper.sakshi.com/Andhra_Pradesh_Main?eid=99&edate=(__holder__)"
    },
    {
        "epaper_name": "andhrajyothy",
        "Epaper_url": "https://epaper.andhrajyothy.com/Home/FullPage?eid=24&edate=(__holder__)"
    }
]

EPAPER_DIRECTORY = {
    item['epaper_name']: item
    for item in epaper_directory_list
}

print(EPAPER_DIRECTORY)