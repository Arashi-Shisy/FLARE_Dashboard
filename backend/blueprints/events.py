from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, session
from extensions import db, scheduler, socketio
from models import Event, EventAttendee, User
from utils.common import serialize_event, parse_iso, serialize_attendee

bp = Blueprint('events', __name__)

def current_user_id():
    return session.get("user_id")

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            return jsonify({"error":"Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

def schedule_event_reminders(event_id):
    ev = Event.query.get(event_id)
    if not ev:
        return
    for hours in (24, 1):
        run_time_utc_naive = ev.start_at - timedelta(hours=hours)
        if run_time_utc_naive < datetime.utcnow():
            continue
        job_id = f"reminder_{event_id}_{hours}h"
        try:
            scheduler.remove_job(job_id)
        except Exception:
            pass
        if not scheduler.running:
            continue
        scheduler.add_job(func=lambda: socketio.emit("event_reminder", {"event_id": event_id, "hours": hours}),
                          trigger="date",
                          run_date=run_time_utc_naive.replace(tzinfo=timezone.utc),
                          id=job_id,
                          replace_existing=True)

@bp.get("/api/events")
@login_required
def list_events():
    include_past = request.args.get("include_past") == "1"
    now = datetime.utcnow()
    q = Event.query
    if not include_past:
        q = q.filter(Event.end_at >= now)
    items = q.order_by(Event.start_at.asc()).all()
    uid = current_user_id()
    res = [serialize_event(e, user_id=uid) for e in items]
    return jsonify({"items": res})

@bp.get("/api/events/thisweek")
@login_required
def list_events_thisweek():
    now = datetime.utcnow()
    start = now - timedelta(days=now.weekday())
    end = start + timedelta(days=7)
    items = Event.query.filter(Event.start_at >= start, Event.start_at < end).all()
    uid = current_user_id()
    res = [serialize_event(e, user_id=uid) for e in items]
    return jsonify({"items": res})

@bp.post("/api/events")
@login_required
def create_event():
    uid = current_user_id()
    data = request.json or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error":"name required"}), 400
    start_at = parse_iso(data.get("start_at"))
    end_at = parse_iso(data.get("end_at"))
    description = data.get("description") or ""
    location = data.get("location") or ""
    url = data.get("url") or ""
    e = Event(name=name, start_at=start_at, end_at=end_at, description=description, location=location, url=url, created_by=uid)
    db.session.add(e)
    db.session.commit()
    att = EventAttendee(user_id=uid, event_id=e.id)
    db.session.add(att)
    db.session.commit()
    schedule_event_reminders(e.id)
    socketio.emit("new_event", serialize_event(e, user_id=uid))
    return jsonify({"message":"created","id": e.id})

@bp.get("/api/events/<int:event_id>")
@login_required
def get_event(event_id):
    uid = current_user_id()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    ev = serialize_event(e, user_id=uid)
    ev["attendee_count"] = EventAttendee.query.filter_by(event_id=event_id).count()
    return jsonify({"event": ev})

@bp.put("/api/events/<int:event_id>")
@login_required
def update_event(event_id):
    uid = current_user_id()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    if e.created_by != uid:
        return jsonify({"error":"forbidden"}), 403
    data = request.json or {}
    if "name" in data:
        e.name = (data["name"] or "").strip() or e.name
    if "start_at" in data:
        e.start_at = parse_iso(data["start_at"]) or e.start_at
    if "end_at" in data:
        e.end_at = parse_iso(data["end_at"]) or e.end_at
    if "description" in data:
        e.description = data["description"] or ""
    if "location" in data:
        e.location = data["location"] or ""
    if "url" in data:
        e.url = data["url"] or ""
    db.session.commit()
    schedule_event_reminders(e.id)
    return jsonify({"message":"updated"})

@bp.delete("/api/events/<int:event_id>")
@login_required
def delete_event(event_id):
    uid = current_user_id()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    if e.created_by != uid:
        return jsonify({"error":"forbidden"}), 403
    EventAttendee.query.filter_by(event_id=event_id).delete()
    db.session.delete(e)
    db.session.commit()
    return jsonify({"message":"deleted"})

@bp.post("/api/events/<int:event_id>/attend")
@login_required
def attend_toggle(event_id):
    uid = current_user_id()
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"not found"}), 404
    att = EventAttendee.query.filter_by(user_id=uid, event_id=event_id).first()
    if att:
        db.session.delete(att)
        db.session.commit()
        return jsonify({"message":"left"})
    else:
        att = EventAttendee(user_id=uid, event_id=event_id)
        db.session.add(att)
        db.session.commit()
        return jsonify({"message":"joined"})

@bp.get("/api/events/<int:event_id>/attendees")
@login_required
def attendees(event_id):
    items = EventAttendee.query.filter_by(event_id=event_id).order_by(EventAttendee.created_at.desc()).all()
    res = [serialize_attendee(a) for a in items]
    return jsonify({"items": res})
