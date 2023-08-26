from . import env


def _send_email(to: str, subject: str, body: str):
    print("------------------------------------")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print()
    print(body)
    print("------------------------------------")


def send_manage_email(to: str, manage_token: str, title: str):
    subject = f"Manage '{title}'"
    body = f"""
    You have created a poll '{title}'.

    To manage, click on the following link:

    {env.BASE_URL}/manage/{manage_token}

    If you don't want to manage, you can ignore this email.
    """

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
