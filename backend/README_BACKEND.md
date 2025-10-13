# Backend Refactor Overview

- Introduced **Blueprints** and **application factory** pattern.
- Split responsibilities:
  - `extensions.py`: shared instances (`db`, `socketio`, `scheduler`)
  - `models.py`: SQLAlchemy models
  - `utils/common.py`: shared helpers/serializers
  - `blueprints/`: feature modules (`auth`, `announcements`, `events`, `chat`, `files`, `misc`)
- Kept **endpoint URLs** and `from app import app, db, init_db` compatibility.
- Scheduler honors `DISABLE_SCHEDULER=1` as before.
