# backend/blueprints/auth.py
# ユーザー登録 / 認証 / プロフィール更新（JSON または アバター画像の multipart）を扱う
from flask import Blueprint, request, jsonify, session, current_app
from passlib.hash import bcrypt
from werkzeug.utils import secure_filename
from extensions import db
from models import User
from utils.common import avatar_url_for
import os

bp = Blueprint('auth', __name__)

# --- セッションから現在のユーザーを取得 ---
def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

# --- ログイン必須デコレータ ---
def login_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user():
            return jsonify({"error":"Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# --- ユーザー登録 ---
@bp.post("/api/register")
def register():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error":"username and password required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error":"username already taken"}), 400
    # bcryptの72byte制限対策（超過時はtruncate）
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

# --- ログイン ---
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

# --- ログアウト ---
@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"ok"})

# --- 自分の情報取得 ---
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

# --- 自分の情報更新 ---
# JSON（プロフィール）と multipart（avatar）を同じエンドポイントで許容する
@bp.post("/api/me")
def update_me():
    u = current_user()
    if not u:
        return jsonify({"error":"Unauthorized"}), 401

    # 1) avatar（multipart/form-data）の場合
    if "avatar" in request.files:
        f = request.files["avatar"]
        if not f or not f.filename:
            return jsonify({"error":"filename required"}), 400
        # mimetype は厳格にせず（application/octet-stream も許容）
        safe = secure_filename(f.filename)
        upload_dir = current_app.config.get("UPLOAD_FOLDER")
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, safe)
        f.save(path)
        u.avatar_path = path
        db.session.commit()
        return jsonify({"message":"updated", "avatar_url": avatar_url_for(u.id, True)})

    # 2) JSON（プロフィール）の場合
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
