"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

from frux_app_server.constants import Category, Stage

db = SQLAlchemy()


class User(db.Model):  # type:ignore
    __tablename__ = 'user'
    __table_args__ = (db.UniqueConstraint('email', name='unique_user_email'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)


class Hashtag(db.Model):  # type:ignore
    __tablename__ = 'hashtag'
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String)
    id_project = db.Column(db.Integer, db.ForeignKey('project.id'))


class Project(db.Model):  # type:ignore
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    goal = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship(User, backref='creator')
    category = db.Column(db.Enum(Category))
    stage = db.Column(db.Enum(Stage))
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
