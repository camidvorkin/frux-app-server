"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

from .graphqlschema.constants import Stage, State

db = SQLAlchemy()


class Investments(db.Model):  # type:ignore
    __tablename__ = 'investments'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    invested_amount = db.Column(db.Float)
    date_of_investment = db.Column(db.DateTime)
    project = db.relationship("Project", back_populates="investors")
    user = db.relationship("User", back_populates="project_investments")


class User(db.Model):  # type:ignore
    __tablename__ = 'user'
    __table_args__ = (db.UniqueConstraint('email', name='unique_user_email'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    image_path = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    project_investments = db.relationship("Investments", back_populates="user")


class HashtagProject(db.Model):  # type:ignore
    __tablename__ = 'hashtag_project'
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtag.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    hashtag = db.relationship("Hashtag", back_populates="projects")
    project = db.relationship("Project", back_populates="hashtags")


class Hashtag(db.Model):  # type:ignore
    __tablename__ = 'hashtag'
    __table_args__ = (db.UniqueConstraint('hashtag', name='unique_hashtag'),)
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String)
    projects = db.relationship("HashtagProject", back_populates="hashtag")


class ProjectStage(db.Model):  # type:ignore
    __tablename__ = 'project_stage'
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.Enum(Stage))
    description = db.Column(db.String)
    goal = db.Column(db.Float)


class Category(db.Model):  # type:ignore
    __tablename__ = 'category'
    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String)


class Project(db.Model):  # type:ignore
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    current_state = db.Column(db.Enum(State))
    goal = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship(User, backref='creator')
    category_name = db.Column(
        db.String, db.ForeignKey('category.name'), default='Other'
    )
    category = db.relationship(Category, backref='projects')
    project_stage_id = db.Column(db.Integer, db.ForeignKey('project_stage.id'))
    stage = db.relationship(ProjectStage, backref='pstage')
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    investors = db.relationship("Investments", back_populates="project")
    hashtags = db.relationship("HashtagProject", back_populates="project")


class Admin(db.Model):  # type:ignore
    __tablename__ = 'admin'
    token = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    user_id = db.Column(db.String)
