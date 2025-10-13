import os
from flask import Blueprint, jsonify, send_from_directory, current_app, request, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType
from models import User
from extensions import db
from utils.common import avatar_url_for

bp = Blueprint('files', __name__)

@bp.errorhandler(RequestEntityTooLarge)
def handle_413(e):
    return jsonify({"error":"File too large"}), 413

@bp.get("/api/avatar/<int:user_id>")
def get_avatar(user_id):
    user = User.query.get(user_id)
    if not user or not user.avatar_path:
        return jsonify({"error":"not found"}), 404
    dirn = os.path.dirname(user.avatar_path)
    fname = os.path.basename(user.avatar_path)
    return send_from_directory(dirn, fname)

@bp.post("/api/me/avatar")
def upload_avatar():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error":"Unauthorized"}), 401
    user = User.query.get(uid)
    if not user:
        return jsonify({"error":"Unauthorized"}), 401
    if "file" not in request.files:
        return jsonify({"error":"file required"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error":"filename required"}), 400
    if not f.mimetype.startswith("image/"):
        raise UnsupportedMediaType()
    safe = secure_filename(f.filename)
    upload_dir = current_app.config.get("UPLOAD_FOLDER") or os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, safe)
    f.save(path)
    user.avatar_path = path
    db.session.commit()
    return jsonify({"message":"uploaded", "avatar_url": avatar_url_for(user.id, True)})
