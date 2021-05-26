import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField

from .filters import FruxFilterableConnectionField
from .object import (
    Admin,
    Hashtag,
    Project,
    ProjectConnections,
    ProjectModel,
    ProjectStage,
    User,
    UserConnections,
    UserModel,
)
from .utils import requires_auth


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    profile = graphene.Field(User)

    @requires_auth
    def resolve_profile(self, info):
        return info.context.user

    user = graphene.Field(User, db_id=graphene.Int())

    def resolve_user(self, info, db_id):  # pylint: disable=unused-argument
        return UserModel.query.get(db_id)

    project = graphene.Field(Project, db_id=graphene.Int())

    def resolve_project(self, info, db_id):  # pylint: disable=unused-argument
        return ProjectModel.query.get(db_id)

    all_users = FruxFilterableConnectionField(UserConnections)
    all_projects = FruxFilterableConnectionField(ProjectConnections)
    all_hashtags = SQLAlchemyConnectionField(Hashtag)
    all_project_stages = SQLAlchemyConnectionField(ProjectStage)
    all_admin = SQLAlchemyConnectionField(Admin)
