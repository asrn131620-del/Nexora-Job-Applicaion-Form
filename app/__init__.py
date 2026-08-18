from flask import Flask
from .db import init_db
from config import SECRET_KEY, MAX_CONTENT_MB, UPLOAD_DIR


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024
    app.config["UPLOAD_DIR"] = str(UPLOAD_DIR)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    init_db()

    from .routes import bp
    app.register_blueprint(bp)

    return app
