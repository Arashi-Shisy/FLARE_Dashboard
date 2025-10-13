from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Announcement, User

bp = Blueprint('announcements', __name__)

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

@bp.get("/api/announcements")
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
        "user_avatar_url": None,
        "created_at": a.created_at.replace(tzinfo=None).isoformat().replace("+00:00","Z")
    } for a in items]
    return jsonify({"items": res})

@bp.post("/api/announcements")
@login_required
def create_ann():
    uid = current_user_id()
    data = request.json or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error":"text required"}), 400
    a = Announcement(text=text, user_id=uid)
    db.session.add(a)
    db.session.commit()
    return jsonify({"message":"created","id": a.id})

@bp.delete("/api/announcements/<int:ann_id>")
@login_required
def delete_ann(ann_id):
    uid = current_user_id()
    a = Announcement.query.get(ann_id)
    if not a:
        return jsonify({"error":"not found"}), 404
    if a.user_id != uid:
        return jsonify({"error":"forbidden"}), 403
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message":"deleted"})
