from flask import Blueprint, request, jsonify, session
from extensions import db, socketio
from models import ChatMessage, User
from utils.common import avatar_url_for

bp = Blueprint('chat', __name__)

def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user():
            return jsonify({"error":"Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

@bp.get("/api/chat")
@login_required
def list_chat():
    items = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(100).all()
    res = [{
        "id": m.id,
        "user_id": m.user_id,
        "user_name": (User.query.get(m.user_id).username if User.query.get(m.user_id) else None),
        "user_avatar_url": avatar_url_for(m.user_id, bool(User.query.get(m.user_id) and User.query.get(m.user_id).avatar_path)),
        "content": m.content,
        "created_at": m.created_at.replace(tzinfo=None).isoformat().replace("+00:00","Z")
    } for m in items]
    return jsonify({"items": res})

@bp.post("/api/chat")
@login_required
def create_chat():
    u = current_user()
    data = request.json or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error":"content required"}), 400
    m = ChatMessage(user_id=u.id, content=content)
    db.session.add(m)
    db.session.commit()
    payload = {
        "id": m.id,
        "user_id": m.user_id,
        "user_name": u.username,
        "user_avatar_url": avatar_url_for(u.id, bool(u.avatar_path)),
        "content": m.content,
        "created_at": m.created_at.replace(tzinfo=None).isoformat().replace("+00:00","Z")
    }
    socketio.emit("chat_message", payload)
    return jsonify({"message":"created","id": m.id, "item": payload})

@bp.delete("/api/chat/<int:msg_id>")
@login_required
def delete_chat(msg_id):
    u = current_user()
    m = ChatMessage.query.get(msg_id)
    if not m:
        return jsonify({"error":"not found"}), 404
    if m.user_id != u.id:
        return jsonify({"error":"forbidden"}), 403
    db.session.delete(m)
    db.session.commit()
    return jsonify({"message":"deleted"})
