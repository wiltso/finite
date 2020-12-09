import smtplib
from email.message import EmailMessage
from django.conf import settings


# Send emails to the persons allowed in the settings
# This can be about how a schedule import when to the daily stats
def sendMail(content, subject="Finites Reporting", whoSent="Finite stats"):
    # Email identification
    EMAIL_SENDER = settings.EMAIL_HOST_USER
    EMAIL_PASSWORD = settings.EMAIL_HOST_PASSWORD

    # Sets the mail information
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = whoSent
    msg['To'] = ', '.join(settings.MAIL_RECEIVERS)

    # Sets the mail content
    msg.set_content(content)

    # Sends the mail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)
