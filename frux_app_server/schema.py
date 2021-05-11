import re

import graphene
import sqlalchemy
from firebase_admin import auth
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphql import GraphQLError
from promise import Promise

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


def requires_auth(func):
    '''
    Authorization decorator for graphql queries/objects.
    Users are authenticated with a Bearer Token given by the firebase app.
    Once authenticated, finds the current user in the database and if
    it doesn't exists it creates it.
    Assigns the current user db object to `info.context.user`.
    '''

    def wrapper(obj, info, **kwargs):
        if 'Authorization' not in info.context.headers:
            raise GraphQLError('Missing Bearer token')
        try:
            userinfo = auth.verify_id_token(
                info.context.headers['Authorization'].split()[-1]
            )
        except auth.ExpiredIdTokenError as e:
            raise GraphQLError('Expired token error') from e
        except auth.InvalidIdTokenError as e:
            raise GraphQLError('Invalid Bearer token') from e
        except auth.TokenSignError as e:
            raise GraphQLError('Token sign error') from e

        try:
            info.context.user = (
                db.session.query(UserModel).filter_by(email=userinfo['email']).one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            info.context.user = UserModel(email=userinfo['email'])
            db.session.add(info.context.user)
            db.session.commit()
        return func(obj, info, **kwargs)

    return wrapper


class CustomSQLAlchemyConnectionField(SQLAlchemyConnectionField):
    @classmethod
    def get_query(cls, model, info, sort=None, **args):
        return requires_auth(super(CustomSQLAlchemyConnectionField, cls).get_query)(
            model, info, sort=sort, **args
        )


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    profile = graphene.Field(User)

    @requires_auth
    def resolve_profile(self, info):
        return info.context.user

    all_users = SQLAlchemyConnectionField(User)
    all_projects = SQLAlchemyConnectionField(Project)


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    def mutate(self, info, name, email):

        if not is_valid_email(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        user = UserModel(name=name, email=email)

        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return Promise.reject(GraphQLError('Email address already registered!'))

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
