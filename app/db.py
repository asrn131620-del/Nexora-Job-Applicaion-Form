import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:

        db_path = Path(
            current_app.config["DATABASE"]
        )

        db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        g.db = sqlite3.connect(
            db_path
        )

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):

    db = g.pop(
        "db",
        None
    )

    if db is not None:
        db.close()


def init_db():

    db = get_db()

    db.execute(
        """
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

            education TEXT NOT NULL,
            institution TEXT,
            graduation_year TEXT,

            experience_level TEXT,
            experience_details TEXT,

            skills TEXT NOT NULL,

            availability TEXT NOT NULL,

            expected_salary TEXT NOT NULL,

            notice_period TEXT,

            declaration INTEGER NOT NULL DEFAULT 0,

            resume_file TEXT NOT NULL,
            photo_file TEXT NOT NULL,
            signature_file TEXT NOT NULL,
            agreement_file TEXT NOT NULL

        )
        """
    )

    db.commit()


def init_app(app):

    app.teardown_appcontext(
        close_db
    )

    with app.app_context():

        init_db()
