import functools

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import Favorites as FavoritesModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import Wallet as WalletModel

from .filters import FruxFilterableConnectionField


class User(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    is_seeder = graphene.Boolean()
    is_sponsor = graphene.Boolean()
    favorite_count = graphene.Int()

    class Meta:
        description = 'Registered users'
        model = UserModel
        interfaces = (graphene.relay.Node,)
        connection_field_factory = FruxFilterableConnectionField.factory

    # User is seeder if has projects
    def resolve_is_seeder(self, info):  # pylint: disable=unused-argument
        return len(self.created_projects) != 0

    # User is sponsor if has investments
    def resolve_is_sponsor(self, info):  # pylint: disable=unused-argument
        return len(self.project_investments)

    def resolve_favorite_count(self, info):  # pylint: disable=unused-argument
        return len(self.favorited_projects)


class UserConnections(graphene.Connection):
    class Meta:
        node = User

    total_count = graphene.Int()

    def resolve_total_count(self, info):  # pylint: disable=unused-argument
        return self.iterable.count()


class ProjectStage(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    class Meta:
        description = 'Registered projects progress stages'
        model = ProjectStageModel
        interfaces = (graphene.relay.Node,)


class Project(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')
    amount_collected = graphene.Int()
    investor_count = graphene.Int()
    favorite_count = graphene.Int()

    class Meta:
        description = 'Registered projects'
        model = ProjectModel
        interfaces = (graphene.relay.Node,)

    def resolve_amount_collected(self, info):  # pylint: disable=unused-argument
        if len(self.investors) == 0:
            return 0
        return functools.reduce(
            lambda a, b: a + b, [i.invested_amount for i in self.investors]
        )

    def resolve_investor_count(self, info):  # pylint: disable=unused-argument
        return len(self.investors)

    def resolve_favorite_count(self, info):  # pylint: disable=unused-argument
        return len(self.favorites_from)


class ProjectConnections(graphene.Connection):
    class Meta:
        node = Project

    total_count = graphene.Int()

    def resolve_total_count(self, info):  # pylint: disable=unused-argument
        return self.iterable.count()


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


class Favorites(SQLAlchemyObjectType):
    class Meta:
        description = 'Favorites from user to project'
        model = FavoritesModel
        interfaces = (graphene.relay.Node,)


class Category(SQLAlchemyObjectType):
    class Meta:
        description = 'Information of the category for projects in the system'
        model = CategoryModel
        interfaces = (graphene.relay.Node,)


class Wallet(SQLAlchemyObjectType):
    class Meta:
        description = 'A wallet given to a user'
        model = WalletModel
        interfaces = (graphene.relay.Node,)
