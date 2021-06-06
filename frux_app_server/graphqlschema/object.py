import functools

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Investments as InvestmentsModel
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
    amount_collected = graphene.Int()

    class Meta:
        description = 'Registered projects'
        model = ProjectModel
        interfaces = (graphene.relay.Node,)

    def resolve_amount_collected(self):
        return functools.reduce(
            lambda a, b: a + b, [i.invested_amount for i in self.investors]
        )


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


class Investments(SQLAlchemyObjectType):
    class Meta:
        description = 'Information of a project backed by a user'
        model = InvestmentsModel
        interfaces = (graphene.relay.Node,)


class Category(SQLAlchemyObjectType):
    class Meta:
        description = 'Information of the category for projects in the system'
        model = CategoryModel
        interfaces = (graphene.relay.Node,)
