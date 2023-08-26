import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_DSN = os.environ.get("DATABASE_DSN")

BASE_URL = os.environ.get("BASE_URL")

SMTP_DISABLE = os.environ.get("SMTP_DISABLE", "false").lower() == "true"

SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))

SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", None)
SMTP_REPLY_TO = os.environ.get("SMTP_REPLY_TO", None)
