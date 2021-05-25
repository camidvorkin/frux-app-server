"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

from .graphqlschema.constants import Category, Stage, State

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


class ProjectStage(db.Model):  # type:ignore
    __tablename__ = 'project_stage'
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Enum(Stage))
    description = db.Column(db.String)
    goal = db.Column(db.Float)


class Project(db.Model):  # type:ignore
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    current_state = db.Column(db.Enum(State))
    goal = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship(User, backref='creator')
    category = db.Column(db.Enum(Category))
    project_stage_id = db.Column(db.Integer, db.ForeignKey('project_stage.id'))
    stage = db.relationship(ProjectStage, backref='pstage')
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)


class Admin(db.Model):  # type:ignore
    __tablename__ = 'admin'
    token = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    user_id = db.Column(db.String)
