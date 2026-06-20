import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

import os


async def send_email(

    to_email: str,

    subject: str,

    body: str
):

    smtp_server = "smtp.gmail.com"

    smtp_port = 587

    sender_email = os.getenv(
        "MAIL_USERNAME"
    )

    sender_password = os.getenv(
        "MAIL_PASSWORD"
    )

    message = MIMEMultipart()

    message["From"] = sender_email

    message["To"] = to_email

    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        server = smtplib.SMTP(
            smtp_server,
            smtp_port
        )

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.sendmail(

            sender_email,

            to_email,

            message.as_string()
        )

        server.quit()

        print(
            f"✅ Email sent to {to_email}"
        )

    except Exception as e:

        print(
            f"❌ Email sending failed: {e}"
        )