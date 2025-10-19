import os
from datetime import timedelta, datetime
from flask import Flask
from flask_cors import CORS
from extensions import db, socketio, scheduler
from blueprints.auth import bp as auth_bp
from blueprints.announcements import bp as ann_bp
from blueprints.events import bp as events_bp
from blueprints.chat import bp as chat_bp
from blueprints.files import bp as files_bp
from blueprints.misc import bp as misc_bp

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///flaredb.sqlite")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", os.environ.get("ASYNC_MODE", "threading"))
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "5"))
DISABLE_SCHEDULER = os.environ.get("DISABLE_SCHEDULER", "0") == "1"
UPLOAD_DIR = os.path.abspath(os.environ.get("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads")))

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
    app.config["MAX_CONTENT_LENGTH"] = 40 * 3840 * 3840
    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

    CORS(app, supports_credentials=True)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode=ASYNC_MODE)

    if not DISABLE_SCHEDULER and not scheduler.running:
        scheduler.start()

    app.register_blueprint(auth_bp)
    app.register_blueprint(ann_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(misc_bp)

    @app.before_request
    def _touch():
        # Session lifetime refresh happens automatically when `permanent` is True.
        pass

    return app

app = create_app()

from models import Event  # for init_db reference

def init_db():
    with app.app_context():
        db.create_all()
        from blueprints.events import schedule_event_reminders
        now = datetime.utcnow()
        upcoming = Event.query.filter(Event.start_at > now).all()
        for e in upcoming:
            schedule_event_reminders(e.id)

if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=8000)
