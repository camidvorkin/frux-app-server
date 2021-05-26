import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel

from .filters import FruxFilterableConnectionField


class User(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    class Meta:
        description = 'Registered users'
        model = UserModel
        interfaces = (graphene.relay.Node,)
        connection_field_factory = FruxFilterableConnectionField.factory


class UserConnections(graphene.Connection):
    class Meta:
        node = User


class ProjectStage(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    class Meta:
        description = 'Registered projects progress stages'
        model = ProjectStageModel
        interfaces = (graphene.relay.Node,)


class Project(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    class Meta:
        description = 'Registered projects'
        model = ProjectModel
        interfaces = (graphene.relay.Node,)


class ProjectConnections(graphene.Connection):
    class Meta:
        node = Project


class Hashtag(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    class Meta:
        description = 'Registered hashtags for projects'
        model = HashtagModel
        interfaces = (graphene.relay.Node,)


class Admin(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered tokens with user information'
        model = AdminModel
        interfaces = (graphene.relay.Node,)
