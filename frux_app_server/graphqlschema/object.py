import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectState as ProjectStateModel
from frux_app_server.models import User as UserModel


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered users'
        model = UserModel
        interfaces = (graphene.relay.Node,)


class ProjectState(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered projects progress states'
        model = ProjectStateModel
        interfaces = (graphene.relay.Node,)


class Project(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered projects'
        model = ProjectModel
        interfaces = (graphene.relay.Node,)


class Hashtag(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered hashtags for projects'
        model = HashtagModel
        interfaces = (graphene.relay.Node,)


class Admin(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered tokens with user information'
        model = AdminModel
        interfaces = (graphene.relay.Node,)
