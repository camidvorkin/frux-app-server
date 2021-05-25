import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField

from .object import Admin, Hashtag, Project, ProjectState, User
from .utils import requires_auth


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    profile = graphene.Field(User)

    @requires_auth
    def resolve_profile(self, info):
        return info.context.user

    all_users = SQLAlchemyConnectionField(User)
    all_projects = SQLAlchemyConnectionField(Project)
    all_hashtags = SQLAlchemyConnectionField(Hashtag)
    all_project_states = SQLAlchemyConnectionField(ProjectState)
    all_admin = SQLAlchemyConnectionField(Admin)
