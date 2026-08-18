import sqlite3
from pathlib import Path
from config import DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    application_id TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'New',

    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,

    dob TEXT,
    gender TEXT,
    city TEXT,
    state TEXT,
    address TEXT,

    position TEXT NOT NULL,
    source TEXT,

    education TEXT,
    institution TEXT,
    graduation_year TEXT,

    experience_level TEXT,
    experience_details TEXT,

    skills TEXT,
    availability TEXT,
    expected_salary TEXT,
    notice_period TEXT,

    declaration INTEGER NOT NULL DEFAULT 0,

    resume_file TEXT NOT NULL,
    photo_file TEXT NOT NULL,
    signature_file TEXT NOT NULL,
    agreement_file TEXT NOT NULL
);
"""


def get_db():
    Path(DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    conn = get_db()

    conn.executescript(SCHEMA)

    conn.commit()
    conn.close()
