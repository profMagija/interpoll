from email.message import EmailMessage
from email.utils import formatdate
import smtplib

from . import env

if not env.SMTP_DISABLE:
    if not env.SMTP_USERNAME or not env.SMTP_PASSWORD or not env.SMTP_EMAIL:
        raise Exception(
            "SMTP_USERNAME, SMTP_PASSWORD, and SMTP_EMAIL must be set if SMTP_DISABLE is false"
        )


def _send_email(to: str, subject: str, body: str):
    if env.SMTP_DISABLE:
        print("------------------------------------")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print()
        print(body)
        print("------------------------------------")
        return

    with smtplib.SMTP(env.SMTP_SERVER, env.SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(env.SMTP_USERNAME, env.SMTP_PASSWORD)

        msg = EmailMessage()
        msg.add_header("From", env.SMTP_FROM or env.SMTP_EMAIL)
        msg.add_header("To", to)
        if env.SMTP_REPLY_TO:
            msg.add_header("Reply-To", env.SMTP_REPLY_TO)
        msg.add_header("Subject", subject)
        msg.add_header("Date", formatdate())
        msg.add_header("Content-Type", "text/plain")
        msg.set_content(body)

        smtp.sendmail(env.SMTP_EMAIL, to, msg.as_bytes())


def send_manage_email(to: str, manage_token: str, observe_token: str, title: str):
    subject = f"Manage '{title}'"
    body = f"""You have created a poll '{title}'.

To manage, click on the following link:

{env.BASE_URL}/manage/{manage_token}

To see the results of the poll, click on the following link:

{env.BASE_URL}/results/{observe_token}

If you don't want to manage, you can ignore this email."""

    _send_email(to, subject, body)


def send_vote_email(to: str, vote_token: str, title: str):
    subject = f"Vote on '{title}'"
    body = f"""
    You have been invited to vote on '{title}'.

    To vote, click on the following link:

    {env.BASE_URL}/vote/{vote_token}

    If you don't want to vote, you can ignore this email.
    """

    _send_email(to, subject, body)
