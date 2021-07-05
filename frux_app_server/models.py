"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

from .graphqlschema.constants import State

db = SQLAlchemy()


class Favorites(db.Model):  # type:ignore
    __tablename__ = 'favorites'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    project = db.relationship("Project", back_populates="favorites_from")
    user = db.relationship("User", back_populates="favorited_projects")


class Investments(db.Model):  # type:ignore
    __tablename__ = 'investments'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    invested_amount = db.Column(db.Float)
    date_of_investment = db.Column(db.DateTime)
    project = db.relationship("Project", back_populates="investors")
    user = db.relationship("User", back_populates="project_investments")


category_association = db.Table(
    'category_association',
    db.Model.metadata,
    db.Column('user', db.Integer, db.ForeignKey('user.id')),
    db.Column('category', db.String, db.ForeignKey('category.name')),
)


class User(db.Model):  # type:ignore
    __tablename__ = 'user'
    __table_args__ = (db.UniqueConstraint('email', name='unique_user_email'),)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    image_path = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    description = db.Column(db.String)
    creation_date_time = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    is_seer = db.Column(db.Boolean)
    seer_projects = db.relationship(
        "Project", back_populates="seer", primaryjoin="User.id==Project.seer_id"
    )
    address = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    phone = db.Column(db.String)
    is_blocked = db.Column(db.Boolean)
    project_investments = db.relationship("Investments", back_populates="user")
    interests = db.relationship("Category", secondary=category_association)
    favorited_projects = db.relationship("Favorites", back_populates="user")


class AssociationHashtag(db.Model):  # type:ignore
    __tablename__ = 'association_hashtag'
    hashtag = db.Column(db.String, db.ForeignKey('hashtag.hashtag'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    hashtag_names = db.relationship("Hashtag")


class Hashtag(db.Model):  # type:ignore
    __tablename__ = 'hashtag'
    __table_args__ = (db.UniqueConstraint('hashtag', name='unique_hashtag'),)
    hashtag = db.Column(db.String, primary_key=True)


class ProjectStage(db.Model):  # type:ignore
    __tablename__ = 'project_stage'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', back_populates="stages")
    title = db.Column(db.String)
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
    owner = db.relationship(User, backref='created_projects', foreign_keys=[user_id])
    category_name = db.Column(
        db.String, db.ForeignKey('category.name'), default='Other'
    )
    category = db.relationship(Category, backref='projects')
    stages = db.relationship(ProjectStage, back_populates="project")
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    investors = db.relationship("Investments", back_populates="project")
    hashtags = db.relationship("AssociationHashtag")
    favorites_from = db.relationship("Favorites", back_populates="project")
    uri_image = db.Column(db.String)
    has_seer = db.Column(db.Boolean)
    seer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seer = db.relationship("User", foreign_keys=[seer_id])


class Admin(db.Model):  # type:ignore
    __tablename__ = 'admin'
    token = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    user_id = db.Column(db.String)
