# backend/blueprints/auth.py
from flask import Blueprint, request, jsonify, session
from passlib.hash import bcrypt
from extensions import db
from models import User
from utils.common import avatar_url_for

bp = Blueprint('auth', __name__)

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

@bp.post("/api/register")
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error":"username already taken"}), 400
    if isinstance(password, str) and len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    pw_hash = bcrypt.hash(password)
    user = User(username=username, pw_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"message":"registered",
                    "user":{"id":user.id,"username":user.username,
                            "avatar_url":avatar_url_for(user.id, bool(user.avatar_path))}})

@bp.post("/api/login")
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.verify(password, user.pw_hash):
        return jsonify({"error":"invalid credentials"}), 400
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"message":"ok",
                    "user":{"id":user.id,"username":user.username,
                            "avatar_url":avatar_url_for(user.id, bool(user.avatar_path))}})

@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"ok"})

@bp.get("/api/me")
def me():
    u = current_user()
    if not u:
        return jsonify({"user": None})
    return jsonify({"user":{
        "id": u.id,
        "username": u.username,
        "avatar_url": avatar_url_for(u.id, bool(u.avatar_path)),
        "birthday": u.birthday,
        "notifications_enabled": bool(u.notifications_enabled),
    }})

@bp.post("/api/me")
def update_me():
    u = current_user()
    if not u:
        return jsonify({"error":"Unauthorized"}), 401
    data = request.json or {}
    if "username" in data:
        name = (data["username"] or "").strip()
        if name and name != u.username:
            if User.query.filter(User.username==name, User.id!=u.id).first():
                return jsonify({"error":"username already taken"}), 400
            u.username = name
    if "birthday" in data:
        u.birthday = data["birthday"] or None
    if "notifications_enabled" in data:
        u.notifications_enabled = bool(data["notifications_enabled"])
    db.session.commit()
    return jsonify({"message":"updated"})
