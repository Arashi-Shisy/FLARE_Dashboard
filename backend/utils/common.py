# backend/utils/common.py
from datetime import datetime, timedelta, timezone
from extensions import db
from models import User, Event, EventAttendee

def iso_z(dt: datetime) -> str:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def parse_iso(s: str) -> datetime:
    if not isinstance(s, str):
        return None
    s2 = s.replace("Z", "+00:00") if isinstance(s, str) else s
    dt = datetime.fromisoformat(s2)
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

def avatar_url_for(user_id: int, has_avatar: bool):
    return f"/api/avatar/{user_id}" if has_avatar else None

def serialize_event(e: Event, user_id=None):
    going = False
    if user_id:
        going = EventAttendee.query.filter_by(user_id=user_id, event_id=e.id).first() is not None
    creator = User.query.get(e.created_by) if e.created_by else None
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
        "created_by_avatar_url": avatar_url_for(creator.id, bool(creator and creator.avatar_path)) if creator else None,
        "created_at": iso_z(e.created_at),
        "going": going
    }

def serialize_attendee(a: EventAttendee):
    u = User.query.get(a.user_id)
    return {
        "id": a.id,
        "user_id": a.user_id,
        "user_name": (u.username if u else None),
        "user_avatar_url": avatar_url_for(a.user_id, bool(u and u.avatar_path)),
        "created_at": iso_z(a.created_at)
    }
