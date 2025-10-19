import os, uuid, io
from flask import Blueprint, jsonify, send_from_directory, current_app, request, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge, UnsupportedMediaType
from PIL import Image, ImageOps, UnidentifiedImageError
import PIL.Image
try:
    import pillow_heif
    pillow_heif.register_heif_opener()  # HEIC/HEIFをPillowで開けるように
except Exception:
    pass

from models import User
from extensions import db
from utils.common import avatar_url_for

bp = Blueprint('files', __name__)

@bp.errorhandler(RequestEntityTooLarge)
def handle_413(e):
    return jsonify({"error":"File too large"}), 413

@bp.errorhandler(UnsupportedMediaType)
def handle_415(e):
    return jsonify({"error":"Unsupported media type"}), 415

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
    if not (f.mimetype.startswith("image/")):
        # 動画やその他は拒否
        raise UnsupportedMediaType()

    # 画像をPillowで開く（HEICも対応）
    try:
        raw = f.read()
        img = Image.open(io.BytesIO(raw))
    except UnidentifiedImageError:
        raise UnsupportedMediaType()

    # EXIFの回転を補正してRGB化
    img = ImageOps.exif_transpose(img).convert("RGB")

    # アバター用に 512x512 にセンタークロップ＆リサイズ
    target = (512, 512)
    img = ImageOps.fit(img, target, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    # 保存先（ユーザーごとにフォルダ分け）
    base_upload = current_app.config.get("UPLOAD_FOLDER") or os.path.join(os.getcwd(), "uploads")
    upload_dir = os.path.join(base_upload, "avatars", str(uid))
    os.makedirs(upload_dir, exist_ok=True)

    # 旧ファイルを掃除（同一ディレクトリ配下のみ消去）
    if user.avatar_path and os.path.commonpath([upload_dir, os.path.dirname(user.avatar_path)]) == upload_dir:
        try:
            if os.path.exists(user.avatar_path):
                os.remove(user.avatar_path)
        except Exception:
            pass

    # WebPで保存（圧縮・最適化）
    filename = f"avatar-{uuid.uuid4().hex}.webp"
    path = os.path.join(upload_dir, filename)
    img.save(path, format="WEBP", quality=80, method=6)

    user.avatar_path = path
    db.session.commit()
    return jsonify({"message":"uploaded", "avatar_url": avatar_url_for(user.id, True)}), 201
