import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField

from .filters import FruxFilterableConnectionField
from .object import (
    Admin,
    Category,
    Hashtag,
    Project,
    ProjectConnections,
    ProjectModel,
    ProjectStage,
    Stats,
    User,
    UserConnections,
    UserModel,
)
from .utils import requires_auth


class Query(graphene.ObjectType,):
    class Meta:
        description = 'Read operations on the database such as getters of specific user or listing all projects or filtering by a criteria'

    node = graphene.relay.Node.Field()

    profile = graphene.Field(
        User, description='Get the profile information about the user'
    )

    @requires_auth
    def resolve_profile(self, info):
        return info.context.user

    user = graphene.Field(User, db_id=graphene.Int())

    def resolve_user(self, info, db_id):  # pylint: disable=unused-argument
        return UserModel.query.get(db_id)

    project = graphene.Field(Project, db_id=graphene.Int())

    def resolve_project(self, info, db_id):  # pylint: disable=unused-argument
        return ProjectModel.query.get(db_id)

    stats = graphene.Field(
        Stats,
        description='Statistics generated about users, projects, invesments, favourites, etc.',
    )

    def resolve_stats(self, _info):
        return []

    all_users = FruxFilterableConnectionField(
        UserConnections, description='All the users are listed'
    )

    all_projects = FruxFilterableConnectionField(
        ProjectConnections, description='All the projects are listed'
    )
    all_hashtags = SQLAlchemyConnectionField(
        Hashtag, description='All used hashtags are listed'
    )
    all_project_stages = SQLAlchemyConnectionField(
        ProjectStage, description='All project stages are listed'
    )
    all_admin = SQLAlchemyConnectionField(
        Admin, description='All registered admins are listed'
    )
    all_categories = SQLAlchemyConnectionField(
        Category, description='All categories of the system are listed'
    )
