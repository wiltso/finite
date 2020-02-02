import smtplib
from email.message import EmailMessage
from django.conf import settings
from django.contrib.auth.models import User


# Send emails to the persons allowd in the settings
# This can be about how a schedule import when to the daily stats
def sendMailToUsers(subject="Sorry for the inconveniences", whoSent="Finite"):
    # Email identification
    EMAIL_SENDER = settings.EMAIL_HOST_USER
    EMAIL_PASSWORD = settings.EMAIL_HOST_PASSWORD

    for user in User.objects.all():

        # Sets the mail informatio
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = whoSent
        msg['To'] = "wilindho@gmail.com, henrikjanssonphoto@gmail.com, richard.borgstrom@eduespoo.fi"

        # Sets the mail content
        msg.set_content("""
Hello everyone!

The holidays have passed and it’s back to school… During the winter break,
most of the Wilma links went out of date, resulting in no schedules shown on your profiles.
We encourage you to re-paste your link into Finite!
It takes under one minute and is super easy to do!
In case you forgot how to do it, you can find the instructions under the “Import your schedule”-tab.

Thank you for using Finite!
The Finite Team""")

        # Sends the mail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
