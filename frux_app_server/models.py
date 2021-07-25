"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

from .graphqlschema.constants import State

db = SQLAlchemy()


class Favorites(db.Model):  # type:ignore
    __tablename__ = 'favorites'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True,
        doc='User\'s ID who add as favourite the project',
    )
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id'),
        primary_key=True,
        doc='Project\'s ID of project that is being added as favourite',
    )
    project = db.relationship("Project", back_populates="favorites_from")
    user = db.relationship("User", back_populates="favorited_projects")


class Investments(db.Model):  # type:ignore
    __tablename__ = 'investments'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True,
        doc='Identifier of the investment',
    )
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    invested_amount = db.Column(
        db.Float,
        doc='Total amount of money invested by the user to the project(as many times as the user invest)',
    )
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
    id = db.Column(db.Integer, primary_key=True, doc='Identifier of the user')
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
        "Project",
        back_populates="seer",
        primaryjoin="User.id==Project.seer_id",
        doc='All projects the user is supervising',
    )
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    is_blocked = db.Column(
        db.Boolean,
        default=False,
        doc='Determines whether the user is blocked by the Backoffice or not',
    )
    project_investments = db.relationship(
        "Investments", back_populates="user", doc='All projects the user invested in'
    )
    interests = db.relationship(
        "Category",
        secondary=category_association,
        doc='All the categories (within Frux system) the user is interested in',
    )
    favorited_projects = db.relationship(
        "Favorites", back_populates="user", doc='All projects the user likes'
    )
    wallet_address = db.Column(
        db.String, db.ForeignKey('wallet.address'), doc='Wallet\'s adress'
    )
    wallet = db.relationship("Wallet", back_populates="user", doc='Own digital wallet')
    reviews = db.relationship(
        "Review",
        back_populates="user",
        doc='Reviews the user gave to projects in which they invested',
    )


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
    project_id = db.Column(
        db.Integer, db.ForeignKey('project.id'), doc='Identifier of the project stage'
    )
    project = db.relationship('Project', back_populates="stages")
    stage_index = db.Column(
        db.Integer, doc='Identification of stage within a project(chronological)'
    )
    title = db.Column(db.String)
    description = db.Column(db.String)
    goal = db.Column(db.Float)
    creation_date = db.Column(db.DateTime)
    funds_released = db.Column(db.Boolean, default=False)
    funds_released_at = db.Column(db.DateTime)


class Category(db.Model):  # type:ignore
    __tablename__ = 'category'
    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String)


class Review(db.Model):  # type:ignore
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', back_populates="reviews")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates="reviews")
    score = db.Column(db.Float, doc='Puntuation given to the project')
    description = db.Column(db.String, doc='Comment given to the project')


class Project(db.Model):  # type:ignore
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, doc='Identifier of the project')
    name = db.Column(db.String)
    description = db.Column(db.String)
    current_state = db.Column(
        db.Enum(State),
        doc='Current status of the project such as: CREATED, FUNDING, IN_PROGRESS, COMPLETE or CANCELED',
    )
    goal = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship(
        User, backref='created_projects', foreign_keys=[user_id], doc='Project creator'
    )
    category_name = db.Column(
        db.String, db.ForeignKey('category.name'), default='Other'
    )
    category = db.relationship(Category, backref='projects')
    stages = db.relationship(
        ProjectStage,
        back_populates="project",
        doc='Division of the project into stages with different objectives and goals. Is required at least one stage',
    )
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    investors = db.relationship(
        "Investments", back_populates="project", doc='All the users that invest in'
    )
    hashtags = db.relationship("AssociationHashtag")
    favorites_from = db.relationship(
        "Favorites", back_populates="project", doc='All the users that like the project'
    )
    uri_image = db.Column(db.String)
    has_seer = db.Column(
        db.Boolean, doc='Determines whether the project has a seer assigned or not'
    )
    seer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seer = db.relationship("User", foreign_keys=[seer_id])
    smart_contract_hash = db.Column(
        db.String, doc='Identificacion of the smart contract created for the project'
    )
    is_blocked = db.Column(
        db.Boolean,
        default=False,
        doc='Determines whether the project is blocked or not',
    )
    creation_date = db.Column(db.DateTime)
    deadline = db.Column(db.DateTime)
    reviews = db.relationship(Review, back_populates="project")


class Admin(db.Model):  # type:ignore
    __tablename__ = 'admin'
    token = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    user_id = db.Column(db.String)


class Wallet(db.Model):  # type:ignore
    __tablename__ = 'wallet'
    address = db.Column(db.String, primary_key=True)
    internal_id = db.Column(db.String)
    user = db.relationship('User', back_populates="wallet")
