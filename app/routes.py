import secrets
import shutil
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from config import (
    FOUNDER_PASSWORD,
    FOUNDER_USERNAME,
    UPLOAD_DIR,
)

from .db import get_db


bp = Blueprint(
    "main",
    __name__
)


STATUSES = [
    "New",
    "Under Review",
    "Shortlisted",
    "Rejected",
]


ALLOWED = {
    "resume": {
        "pdf",
        "doc",
        "docx",
    },

    "photo": {
        "jpg",
        "jpeg",
        "png",
        "webp",
    },

    "signature": {
        "jpg",
        "jpeg",
        "png",
        "webp",
    },

    "agreement": {
        "pdf",
    },
}


def allowed_file(filename, file_type):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED[file_type]
    )


def founder_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):

        if not session.get("founder"):
            return redirect(
                url_for("main.founder_login")
            )

        return view(*args, **kwargs)

    return wrapped


def new_application_id():

    db = get_db()

    while True:

        application_id = (
            "NX-"
            + datetime.now().strftime("%Y%m%d")
            + "-"
            + secrets.token_hex(3).upper()
        )

        existing = db.execute(
            """
            SELECT 1
            FROM applications
            WHERE application_id = ?
            """,
            (application_id,),
        ).fetchone()

        if not existing:
            return application_id


def save_upload(file, application_id, file_type):

    if not file or not file.filename:
        raise ValueError(
            f"Please upload your "
            f"{file_type.replace('_', ' ')}."
        )

    if not allowed_file(
        file.filename,
        file_type
    ):
        allowed = ", ".join(
            sorted(ALLOWED[file_type])
        )

        raise ValueError(
            f"Invalid "
            f"{file_type.replace('_', ' ')} "
            f"format. Allowed: {allowed}."
        )

    original_name = secure_filename(
        file.filename
    )

    if not original_name:
        raise ValueError(
            f"Invalid {file_type.replace('_', ' ')} filename."
        )

    suffix = Path(
        original_name
    ).suffix.lower()

    folder = (
        Path(UPLOAD_DIR)
        / application_id
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{file_type}{suffix}"
    )

    file.save(
        folder / filename
    )

    return (
        f"{application_id}/{filename}"
    )


@bp.get("/")
def home():

    return render_template(
        "form.html"
    )


@bp.post("/apply")
def apply():

    form = request.form

    required_fields = [
        "full_name",
        "email",
        "phone",
        "position",
        "education",
        "skills",
        "availability",
        "expected_salary",
    ]

    missing = [
        field
        for field in required_fields
        if not form.get(field, "").strip()
    ]

    if missing:

        flash(
            "Please complete all required fields.",
            "error"
        )

        return redirect(
            url_for("main.home")
        )

    if form.get("declaration") != "on":

        flash(
            "Please accept the declaration.",
            "error"
        )

        return redirect(
            url_for("main.home")
        )

    application_id = new_application_id()

    try:

        resume = save_upload(
            request.files.get("resume"),
            application_id,
            "resume"
        )

        photo = save_upload(
            request.files.get("photo"),
            application_id,
            "photo"
        )

        signature = save_upload(
            request.files.get("signature"),
            application_id,
            "signature"
        )

        agreement = save_upload(
            request.files.get("agreement"),
            application_id,
            "agreement"
        )

        db = get_db()

        db.execute(
            """
            INSERT INTO applications (

                application_id,
                created_at,
                status,

                full_name,
                email,
                phone,

                dob,
                gender,
                city,
                state,
                address,

                position,
                source,

                education,
                institution,
                graduation_year,

                experience_level,
                experience_details,

                skills,
                availability,
                expected_salary,
                notice_period,

                declaration,

                resume_file,
                photo_file,
                signature_file,
                agreement_file

            )

            VALUES (
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?,
                ?, ?, ?, ?
            )
            """,
            (
                application_id,

                datetime.now(
                    timezone.utc
                ).isoformat(),

                "New",

                form.get("full_name").strip(),
                form.get("email").strip(),
                form.get("phone").strip(),

                form.get("dob"),
                form.get("gender"),
                form.get("city"),
                form.get("state"),
                form.get("address"),

                form.get("position").strip(),
                form.get("source"),

                form.get("education").strip(),
                form.get("institution"),
                form.get("graduation_year"),

                form.get("experience_level"),
                form.get("experience_details"),

                form.get("skills").strip(),
                form.get("availability"),
                form.get("expected_salary").strip(),
                form.get("notice_period"),

                1,

                resume,
                photo,
                signature,
                agreement,
            )
        )

        db.commit()

    except Exception as error:

        shutil.rmtree(
            Path(UPLOAD_DIR)
            / application_id,
            ignore_errors=True
        )

        flash(
            "Application could not be submitted. "
            "Please check your files and try again.",
            "error"
        )

        return redirect(
            url_for("main.home")
        )

    return render_template(
        "success.html",
        application_id=application_id,
        name=form.get("full_name")
    )


@bp.get("/agreement")
def agreement():

    project_root = Path(
        __file__
    ).resolve().parent.parent

    agreement_path = (
        project_root
        / "app"
        / "static"
        / "docs"
        / "employment-agreement.pdf"
    )

    if not agreement_path.is_file():

        return render_template(
            "agreement_missing.html"
        ), 404

    return send_from_directory(
        agreement_path.parent,
        agreement_path.name,
        as_attachment=False
    )


@bp.route(
    "/founder/login",
    methods=["GET", "POST"]
)
def founder_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        if (
            FOUNDER_USERNAME
            and FOUNDER_PASSWORD
            and secrets.compare_digest(
                username,
                FOUNDER_USERNAME
            )
            and secrets.compare_digest(
                password,
                FOUNDER_PASSWORD
            )
        ):

            session["founder"] = True

            return redirect(
                url_for("main.dashboard")
            )

        flash(
            "Invalid founder credentials.",
            "error"
        )

    return render_template(
        "login.html"
    )


@bp.get("/founder/logout")
def founder_logout():

    session.clear()

    return redirect(
        url_for("main.founder_login")
    )


@bp.get("/founder")
@founder_required
def dashboard():

    query = request.args.get(
        "q",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    db = get_db()

    sql = """
        SELECT *
        FROM applications
        WHERE 1 = 1
    """

    params = []

    if query:

        sql += """
            AND (
                full_name LIKE ?
                OR email LIKE ?
                OR application_id LIKE ?
                OR phone LIKE ?
            )
        """

        search = f"%{query}%"

        params.extend(
            [
                search,
                search,
                search,
                search,
            ]
        )

    if status in STATUSES:

        sql += """
            AND status = ?
        """

        params.append(status)

    sql += """
        ORDER BY id DESC
    """

    applications = db.execute(
        sql,
        params
    ).fetchall()

    return render_template(
        "dashboard.html",
        applications=applications,
        statuses=STATUSES,
        q=query,
        status=status
    )


@bp.post(
    "/founder/application/<int:row_id>/status"
)
@founder_required
def update_status(row_id):

    new_status = request.form.get(
        "status"
    )

    if new_status not in STATUSES:

        abort(400)

    db = get_db()

    db.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE id = ?
        """,
        (
            new_status,
            row_id
        )
    )

    db.commit()

    return redirect(
        request.referrer
        or url_for("main.dashboard")
    )


@bp.get(
    "/founder/application/<int:row_id>"
)
@founder_required
def application_detail(row_id):

    db = get_db()

    application = db.execute(
        """
        SELECT *
        FROM applications
        WHERE id = ?
        """,
        (row_id,)
    ).fetchone()

    if not application:

        abort(404)

    return render_template(
        "detail.html",
        a=application
    )


@bp.get(
    "/founder/file/<int:row_id>/<kind>"
)
@founder_required
def protected_file(row_id, kind):

    allowed_types = {
        "resume",
        "photo",
        "signature",
        "agreement",
    }

    if kind not in allowed_types:

        abort(404)

    db = get_db()

    application = db.execute(
        """
        SELECT *
        FROM applications
        WHERE id = ?
        """,
        (row_id,)
    ).fetchone()

    if not application:

        abort(404)

    relative_path = application[
        f"{kind}_file"
    ]

    try:
        folder, filename = (
            relative_path.split("/", 1)
        )
    except ValueError:
        abort(404)

    return send_from_directory(
        Path(UPLOAD_DIR) / folder,
        filename,
        as_attachment=False
    )
