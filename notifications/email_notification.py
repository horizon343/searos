import smtplib, ssl
import os

from dotenv import load_dotenv


def send_email(receiver_email, subject, message_text):
    load_dotenv()

    port = int(os.environ["SMTP_PORT"])
    smtp_server = os.environ["SMTP_SERVER"]
    sender_email = os.environ["SMTP_SENDER_EMAIL"]
    password = os.environ["SMTP_PASSWORD"]

    message = f"""Subject: {subject}
              {message_text}"""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

        print("letter sent")
