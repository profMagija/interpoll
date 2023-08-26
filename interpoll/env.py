import os

DATABASE_DSN = os.environ.get(
    "DATABASE_DSN",
    "host=localhost port=5432 dbname=interpoll user=interpoll password=interpoll",
)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
