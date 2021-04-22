"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TodoSimple(db.Model):  # type:ignore
    id = db.Column(db.Integer, primary_key=True)
    reminder = db.Column(db.String)
