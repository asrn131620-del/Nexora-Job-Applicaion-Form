 from flask import Flask

from config import (
    SECRET_KEY,
    MAX_CONTENT_MB,
    UPLOAD_DIR,
    DATABASE_PATH,
)

from .db import init_app


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config["SECRET_KEY"] = SECRET_KEY

    app.config["MAX_CONTENT_LENGTH"] = (
        MAX_CONTENT_MB * 1024 * 1024
    )

    app.config["UPLOAD_DIR"] = str(
        UPLOAD_DIR
    )

    app.config["DATABASE"] = DATABASE_PATH

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    init_app(app)

    from .routes import bp

    app.register_blueprint(bp)

    return app
