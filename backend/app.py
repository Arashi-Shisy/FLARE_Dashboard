import os
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_socketio import SocketIO, emit
from passlib.hash import bcrypt
from werkzeug.utils import secure_filename

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///flaredb.sqlite")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "eventlet")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
UPLOAD_DIR = os.path.abspath(os.environ.get("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads")))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

CORS(app, supports_credentials=True)

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=ASYNC_MODE)

scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
scheduler.start()

def now_jst():
    return datetime.utcnow() + timedelta(hours=9)

def iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def parse_iso(s: str) -> datetime:
    if not isinstance(s, str):
        raise ValueError("datetime string required")
    s2 = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s2)
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

def avatar_url_for(user_id: int, has_avatar: bool):
    return f"/api/avatar/{user_id}" if has_avatar else None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(255), nullable=False)
    avatar_path = db.Column(db.String(255))
    birthday = db.Column(db.String(10))
    notifications_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(255), default="")
    url = db.Column(db.String(255), default="")
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventAttendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_attend'), )

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user():
            return jsonify({"error":"Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

def schedule_event_reminders(event_id):
    ev = Event.query.get(event_id)
    if not ev:
        return
    for hours in (24, 1):
        run_time = ev.start_at - timedelta(hours=hours)
        if run_time > datetime.utcnow():
            job_id = f"reminder_{event_id}_{hours}h"
            try:
                scheduler.remove_job(job_id)
            except Exception:
                pass
            scheduler.add_job(func=emit_event_reminder, trigger="date",
                              run_date=run_time, id=job_id,
                              args=[event_id, hours])

def emit_event_reminder(event_id, hours):
    attendees = EventAttendee.query.filter_by(event_id=event_id).all()
    user_ids = [a.user_id for a in attendees]
    socketio.emit("event_reminder", {"event_id": event_id, "hours": hours, "user_ids": user_ids})

def serialize_event(e, user_id=None):
    going = False
    if user_id:
        going = EventAttendee.query.filter_by(event_id=e.id, user_id=user_id).first() is not None
    creator = User.query.get(e.created_by)
    return {
        "id": e.id,
        "name": e.name,
        "start_at": iso_z(e.start_at),
        "end_at": iso_z(e.end_at),
        "description": e.description,
        "location": e.location,
        "url": e.url,
        "created_by": e.created_by,
        "created_by_name": (creator.username if creator else None),
        "created_by_avatar_url": avatar_url_for(creator.id, bool(creator and creator.avatar_path)),
        "created_at": iso_z(e.created_at),
        "going": going
    }

def serialize_attendee(a: EventAttendee):
    u = User.query.get(a.user_id)
    return {
        "user_id": a.user_id,
        "user_name": (u.username if u else None),
        "avatar_url": avatar_url_for(a.user_id, bool(u and u.avatar_path)),
        "joined_at": iso_z(a.created_at),
    }

@app.post("/api/register")
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error":"username already taken"}), 400
    pw_hash = bcrypt.hash(password)
    user = User(username=username, pw_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"message":"registered","user":{"id":user.id,"username":user.username,"avatar_url":avatar_url_for(user.id, bool(user.avatar_path))}})

@app.post("/api/login")
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.verify(password, user.pw_hash):
        return jsonify({"error":"invalid credentials"}), 401
    session["user_id"] = user.id
    session.permanent = True
    user.last_active_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message":"logged_in","user":{"id":user.id,"username":user.username,"avatar_url":avatar_url_for(user.id, bool(user.avatar_path))}})

@app.get("/api/me")
def me():
    user = current_user()
    if not user:
        return jsonify({"user": None})
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "avatar_url": avatar_url_for(user.id, bool(user.avatar_path)),
            "birthday": user.birthday,
            "notifications_enabled": user.notifications_enabled
        }
    })

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"logged_out"})

@app.post("/api/me")
@login_required
def update_me():
    user = current_user()
    if request.files:
        f = request.files.get("avatar")
        if f and f.filename:
            filename = secure_filename(f.filename)
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
            filename = f"user_{user.id}_avatar.{ext}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            f.save(path)
            user.avatar_path = path
    data = request.form if request.form else (request.json or {})
    birthday = data.get("birthday")
    notifications_enabled = data.get("notifications_enabled")
    if birthday is not None:
        user.birthday = birthday
    if notifications_enabled is not None:
        user.notifications_enabled = bool(str(notifications_enabled).lower() in ("1","true","yes","on"))
    user.last_active_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message":"updated","avatar_url": avatar_url_for(user.id, bool(user.avatar_path))})

@app.get("/api/avatar/<int:user_id>")
def get_avatar(user_id):
    u = User.query.get(user_id)
    if not u or not u.avatar_path or not os.path.exists(u.avatar_path):
        return jsonify({"error":"not found"}), 404
    dirn, fname = os.path.split(u.avatar_path)
    return send_from_directory(dirn, fname)

@app.get("/api/announcements")
@login_required
def list_ann():
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    items = Announcement.query.order_by(Announcement.created_at.desc()).offset(offset).limit(limit).all()
    res = [{
        "id": a.id,
        "text": a.text,
        "user_id": a.user_id,
        "user_name": (User.query.get(a.user_id).username if User.query.get(a.user_id) else None),
        "user_avatar_url": avatar_url_for(a.user_id, bool(User.query.get(a.user_id) and User.query.get(a.user_id).avatar_path)),
        "created_at": iso_z(a.created_at)
    } for a in items]
    return jsonify({"items": res})

@app.post("/api/announcements")
@login_required
def create_ann():
    user = current_user()
    data = request.json or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error":"text required"}), 400
    a = Announcement(text=text, user_id=user.id)
    db.session.add(a)
    db.session.commit()
    payload = {
        "id": a.id,
        "text": a.text,
        "user_id": a.user_id,
        "user_name": user.username,
        "user_avatar_url": avatar_url_for(user.id, bool(user.avatar_path)),
        "created_at": iso_z(a.created_at)
    }
    socketio.emit("new_announcement", payload)
    return jsonify({"message":"created","id":a.id, "item": payload})

@app.delete("/api/announcements/<int:ann_id>")
@login_required
def delete_ann(ann_id):
    user = current_user()
    a = Announcement.query.get(ann_id)
    if not a:
        return jsonify({"error":"not found"}), 404
    if a.user_id != user.id:
        return jsonify({"error":"forbidden"}), 403
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message":"deleted"})

@app.get("/api/events")
@login_required
def list_events():
    user = current_user()
    upcoming = request.args.get("upcoming", "true").lower() != "false"
    include_past = request.args.get("include_past", "false").lower() == "true"
    q = Event.query
    now = datetime.utcnow()
    if upcoming and not include_past:
        q = q.filter(Event.end_at >= now)
    items = q.order_by(Event.start_at.asc()).all()
    res = [serialize_event(e, user_id=user.id) for e in items]
    return jsonify({"items": res})

@app.get("/api/events/thisweek")
@login_required
def events_this_week():
    user = current_user()
    jst_now = now_jst()
    start = jst_now - timedelta(days=jst_now.weekday())
    end = start + timedelta(days=7)
    start_utc = start - timedelta(hours=9)
    end_utc = end - timedelta(hours=9)
    items = Event.query.filter(Event.start_at >= start_utc, Event.start_at < end_utc).order_by(Event.start_at.asc()).all()
    res = [serialize_event(e, user_id=user.id) for e in items]
    return jsonify({"items": res})

@app.post("/api/events")
@login_required
def create_event():
    user = current_user()
    data = request.json or {}
    try:
        name = (data.get("name") or "").strip()
        start_at = parse_iso(data["start_at"])
        end_at   = parse_iso(data["end_at"])
    except Exception:
        return jsonify({"error":"invalid payload"}), 400
    if not name:
        return jsonify({"error":"name required"}), 400
    ev = Event(name=name, start_at=start_at, end_at=end_at,
               description=data.get("description",""),
               location=data.get("location",""),
               url=data.get("url",""),
               created_by=user.id)
    db.session.add(ev)
    db.session.commit()
    att = EventAttendee(user_id=user.id, event_id=ev.id)
    db.session.add(att)
    db.session.commit()
    schedule_event_reminders(ev.id)
    socketio.emit("new_event", serialize_event(ev, user_id=user.id))
    return jsonify({"message":"created","id": ev.id})

@app.get("/api/events/<int:event_id>")
@login_required
def get_event(event_id):
    user = current_user()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    ev = serialize_event(e, user_id=user.id)
    ev["attendee_count"] = EventAttendee.query.filter_by(event_id=event_id).count()
    return jsonify({"event": ev})

@app.put("/api/events/<int:event_id>")
@login_required
def update_event(event_id):
    user = current_user()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    if e.created_by != user.id:
        return jsonify({"error":"forbidden"}), 403
    data = request.json or {}
    if "name" in data:
        e.name = (data["name"] or "").strip() or e.name
    if "start_at" in data:
        e.start_at = parse_iso(data["start_at"])
    if "end_at" in data:
        e.end_at = parse_iso(data["end_at"])
    if "description" in data:
        e.description = data["description"] or ""
    if "location" in data:
        e.location = data["location"] or ""
    if "url" in data:
        e.url = data["url"] or ""
    db.session.commit()
    schedule_event_reminders(e.id)
    return jsonify({"message":"updated"})

@app.delete("/api/events/<int:event_id>")
@login_required
def delete_event(event_id):
    user = current_user()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    if e.created_by != user.id:
        return jsonify({"error":"forbidden"}), 403
    EventAttendee.query.filter_by(event_id=event_id).delete()
    db.session.delete(e)
    db.session.commit()
    for hours in (24,1):
        try:
            scheduler.remove_job(f"reminder_{event_id}_{hours}h")
        except Exception:
            pass
    return jsonify({"message":"deleted"})

@app.post("/api/events/<int:event_id>/attend")
@login_required
def toggle_attend(event_id):
    user = current_user()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    att = EventAttendee.query.filter_by(event_id=event_id, user_id=user.id).first()
    going = False
    if att:
        db.session.delete(att)
        going = False
    else:
        db.session.add(EventAttendee(user_id=user.id, event_id=event_id))
        going = True
    db.session.commit()
    count = EventAttendee.query.filter_by(event_id=event_id).count()
    return jsonify({"message":"toggled","going":going,"attendee_count":count})

@app.get("/api/events/<int:event_id>/attendees")
@login_required
def event_attendees(event_id):
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error": "not found"}), 404
    rows = EventAttendee.query.filter_by(event_id=event_id)\
        .order_by(EventAttendee.created_at.asc()).all()
    return jsonify({
        "items": [serialize_attendee(a) for a in rows],
        "count": len(rows)
    })

@app.get("/api/chat")
@login_required
def list_chat():
    limit = int(request.args.get("limit", 50))
    items = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(limit).all()
    res = [{
        "id": m.id,
        "user_id": m.user_id,
        "user_name": (User.query.get(m.user_id).username if User.query.get(m.user_id) else None),
        "user_avatar_url": avatar_url_for(m.user_id, bool(User.query.get(m.user_id) and User.query.get(m.user_id).avatar_path)),
        "content": m.content,
        "created_at": iso_z(m.created_at)
    } for m in items]
    return jsonify({"items": res})

@app.post("/api/chat")
@login_required
def create_chat():
    user = current_user()
    data = request.json or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error":"content required"}), 400
    m = ChatMessage(user_id=user.id, content=content)
    db.session.add(m)
    db.session.commit()
    payload = {
        "id": m.id,
        "user_id": m.user_id,
        "user_name": user.username,
        "user_avatar_url": avatar_url_for(user.id, bool(user.avatar_path)),
        "content": m.content,
        "created_at": iso_z(m.created_at)
    }
    socketio.emit("chat_message", payload)
    return jsonify({"message":"created","id": m.id, "item": payload})

@app.delete("/api/chat/<int:msg_id>")
@login_required
def delete_chat(msg_id):
    user = current_user()
    m = ChatMessage.query.get(msg_id)
    if not m:
        return jsonify({"error":"not found"}), 404
    if m.user_id != user.id:
        return jsonify({"error":"forbidden"}), 403
    db.session.delete(m)
    db.session.commit()
    return jsonify({"message":"deleted"})

@app.get("/api/home")
@login_required
def home():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    ann_res = [{
        "id": a.id,
        "text": a.text,
        "user_id": a.user_id,
        "user_name": (User.query.get(a.user_id).username if User.query.get(a.user_id) else None),
        "user_avatar_url": avatar_url_for(a.user_id, bool(User.query.get(a.user_id) and User.query.get(a.user_id).avatar_path)),
        "created_at": iso_z(a.created_at)
    } for a in anns]
    user = current_user()
    jst_now = now_jst()
    start = jst_now - timedelta(days=jst_now.weekday())
    end = start + timedelta(days=7)
    start_utc = start - timedelta(hours=9)
    end_utc = end - timedelta(hours=9)
    events = Event.query.filter(Event.start_at >= start_utc, Event.start_at < end_utc).order_by(Event.start_at.asc()).all()
    ev_res = [serialize_event(e, user_id=user.id) for e in events]
    return jsonify({"announcements": ann_res, "events": ev_res})

@socketio.on("connect")
def sio_connect():
    emit("connected", {"message":"ok"})

@app.get("/api/health")
def health():
    return jsonify({"status":"ok"})

def init_db():
    db.create_all()
    now = datetime.utcnow()
    upcoming = Event.query.filter(Event.start_at > now).all()
    for e in upcoming:
        schedule_event_reminders(e.id)

@app.before_request
def touch_last_active():
    if "user_id" in session:
        session.permanent = True

if __name__ == "__main__":
    with app.app_context():
        init_db()
    socketio.run(app, host="0.0.0.0", port=8000)
