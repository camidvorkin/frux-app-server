import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField

from .filters import FruxFilterableConnectionField
from .object import Admin, Hashtag, Project, ProjectStage, User, UserConnection
from .utils import requires_auth


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    profile = graphene.Field(User)

    @requires_auth
    def resolve_profile(self, info):
        return info.context.user

    all_users = FruxFilterableConnectionField(UserConnection)
    all_projects = SQLAlchemyConnectionField(Project)
    all_hashtags = SQLAlchemyConnectionField(Hashtag)
    all_project_stages = SQLAlchemyConnectionField(ProjectStage)
    all_admin = SQLAlchemyConnectionField(Admin)
