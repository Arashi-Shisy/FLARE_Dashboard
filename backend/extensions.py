# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
socketio = SocketIO()
scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
