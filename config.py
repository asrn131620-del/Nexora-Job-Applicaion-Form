import os
from pathlib import Path


BASE_DIR = Path(
    __file__
).resolve().parent


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    str(
        BASE_DIR
        / "instance"
        / "nexora.sqlite3"
    )
)


UPLOAD_DIR = Path(
    os.getenv(
        "UPLOAD_DIR",
        str(
            BASE_DIR
            / "uploads"
        )
    )
)


MAX_CONTENT_MB = int(
    os.getenv(
        "MAX_CONTENT_MB",
        "10"
    )
)


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    ""
)


FOUNDER_USERNAME = os.getenv(
    "FOUNDER_USERNAME",
    ""
)


FOUNDER_PASSWORD = os.getenv(
    "FOUNDER_PASSWORD",
    ""
)
