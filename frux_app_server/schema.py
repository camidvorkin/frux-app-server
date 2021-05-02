import re

import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphql import GraphQLError

from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db

# pylint: disable=unused-argument


def is_valid_email(email):
    return re.match(
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
        email,
    )


class User(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered users'
        model = UserModel
        interfaces = (graphene.relay.Node,)


class Project(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered projects'
        model = ProjectModel
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    def resolve_users(self, info, name=None):
        query = User.get_query(info)
        if name:
            query = query.filter(UserModel.name == name)
        return query.all()

    all_users = SQLAlchemyConnectionField(User)
    all_projects = SQLAlchemyConnectionField(Project)


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    def mutate(self, info, name, email):

        if not is_valid_email(email):
            raise GraphQLError('Invalid email address!')

        user = UserModel(name=name, email=email)

        db.session.add(user)
        db.session.commit()

        # 200 OK
        return UserMutation(user=user)


class ProjectMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        goal = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    project = graphene.Field(lambda: Project)

    def mutate(self, info, user_id, name, description, goal):
        user = UserModel.query.get(user_id)

        project = ProjectModel(
            name=name, description=description, goal=goal, owner=user
        )

        db.session.add(project)
        db.session.commit()

        return ProjectMutation(project=project)


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
