import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import *

SUBJECT = "E-paper delivery system"

def send_email_with_pdf(receiver, pdf_path):

    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = receiver
    message['Subject'] = SUBJECT

    body = (
        "Thank you for reaching me out for the E-paper. As this is a demo project, "
        "the requested E-paper is compressed. Please visit the respective e-paper sites "
        "to access the e-paper in full quality. \n\n"
        "If you have any queries please contact me on +2149409064 / "
        "kawsshikhsajjan7@gmail.com / https://www.linkedin.com/in/kawsshikh/ \n\n"
        "Thank You"
    )

    message.attach(MIMEText(body, 'plain'))

    try:

        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        filename = os.path.basename(pdf_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        message.attach(part)
        print(f"Attachment successfully prepared: {filename}")

    except FileNotFoundError:
        print(f"Error: Attachment file not found at {pdf_path}")
        return
    except Exception as e:
        print(f"Error preparing attachment: {e}")
        return

    try:

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

            server.starttls()
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, receiver, message.as_string())
            print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Check your email and App Password/credentials.")
    except Exception as e:
        print(f"An error occurred during email transmission: {e}")

