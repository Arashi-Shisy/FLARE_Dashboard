from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from models import Announcement, Event
from utils.common import serialize_event

bp = Blueprint('misc', __name__)

@bp.get("/api/home")
def home():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    ann_res = [{
        "id": a.id,
        "text": a.text,
        "user_id": a.user_id,
        "created_at": a.created_at.replace(tzinfo=None).isoformat().replace("+00:00","Z")
    } for a in anns]

    now = datetime.utcnow()
    start = now - timedelta(days=now.weekday())
    end = start + timedelta(days=7)
    evs = Event.query.filter(Event.start_at >= start, Event.start_at < end).all()
    ev_res = [serialize_event(e) for e in evs]

    return jsonify({"announcements": ann_res, "events": ev_res})

@bp.get("/api/health")
def health():
    return jsonify({"status":"ok"})
