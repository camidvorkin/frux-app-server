import datetime
import functools

import graphene
from firebase_admin import storage
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.filters import FruxFilterableConnectionField
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import AssociationHashtag as AssociationHashtagModel
from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import Favorites as FavoritesModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import Review as ReviewModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import Wallet as WalletModel
from frux_app_server.models import db
from frux_app_server.services.smart_contract_client import smart_contract_client


class User(SQLAlchemyObjectType):
    db_id = graphene.Int(source='id')

    is_seeder = graphene.Boolean()
    is_sponsor = graphene.Boolean()
    favorite_count = graphene.Int()
    wallet_private_key = graphene.String()

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

    @requires_auth
    def resolve_wallet_private_key(self, info):  # pylint: disable=unused-argument
        if info.context.user.id != self.id:
            return Promise.reject(GraphQLError('Unauthorized'))
        return smart_contract_client.get_private_key(self.wallet.internal_id)


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
    amount_collected = graphene.Float()
    investor_count = graphene.Int()
    favorite_count = graphene.Int()
    general_score = graphene.Float()
    review_count = graphene.Int()
    signed_url = graphene.String()

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

    def resolve_general_score(self, info):  # pylint: disable=unused-argument
        if len(self.reviews) == 0:
            return 0
        return functools.reduce(
            lambda a, b: a + b, [r.score for r in self.reviews]
        ) / len(self.reviews)

    def resolve_review_count(self, info):  # pylint: disable=unused-argument
        return len(self.reviews)

    def resolve_signed_url(self, _info):
        key = self.uri_image
        if not key:
            key = 'nopicture.jpg'
        bucket = storage.bucket('frux-mobile.appspot.com')
        blob = bucket.blob(key)
        url = blob.generate_signed_url(expiration=datetime.timedelta(minutes=30))
        return url


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
    balance = graphene.Float()

    class Meta:
        description = 'A wallet given to a user'
        model = WalletModel
        interfaces = (graphene.relay.Node,)

    def resolve_balance(self, info):  # pylint: disable=unused-argument
        return smart_contract_client.get_wallet_balance(self.internal_id)


class AssociationHashtag(SQLAlchemyObjectType):
    class Meta:
        description = 'Associates each hashtag from each project'
        model = AssociationHashtagModel
        interfaces = (graphene.relay.Node,)


class Review(SQLAlchemyObjectType):
    class Meta:
        description = 'Review of a project'
        model = ReviewModel
        interfaces = (graphene.relay.Node,)


class Stats(graphene.ObjectType):
    class Meta:
        description = 'General stats of frux-app-server'
        interfaces = (graphene.relay.Node,)

    total_users = graphene.Int(description='Total users in the system')
    total_seers = graphene.Int(description='Total seers in the system')
    total_projects = graphene.Int(description='Total projects in the system')
    total_favorites = graphene.Int(description='Total favorites in the system')
    total_investments = graphene.Int(description='Total investments in the system')
    total_hashtags = graphene.Int(description='Total hashtags in the system')

    def resolve_total_users(self, _info):
        return db.session.query(UserModel).count()

    def resolve_total_seers(self, _info):
        return db.session.query(UserModel).filter(UserModel.is_seer).count()

    def resolve_total_projects(self, _info):
        return db.session.query(ProjectModel).count()

    def resolve_total_favorites(self, _info):
        return db.session.query(FavoritesModel).count()

    def resolve_total_investments(self, _info):
        return db.session.query(InvestmentsModel).count()

    def resolve_total_hashtags(self, _info):
        return db.session.query(HashtagModel).count()
