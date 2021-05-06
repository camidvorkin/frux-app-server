import re

import graphene
import sqlalchemy
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from graphql import GraphQLError
from promise import Promise

from frux_app_server.constants import Category, Stage, categories, stages
from frux_app_server.models import Hashtag as HashtagModel
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


class Hashtag(SQLAlchemyObjectType):
    class Meta:
        description = 'Registered projects'
        model = HashtagModel
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
    all_hashtags = SQLAlchemyConnectionField(Hashtag)


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
        hashtags = graphene.List(graphene.String)
        category = graphene.String()
        stage = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()

    project = graphene.Field(lambda: Project)

    def mutate(
        self,
        info,
        user_id,
        name,
        description,
        goal,
        hashtags,
        category=(Category.OTHERS.value),
        stage=(Stage.IN_PROGRESS.value),
        latitude="0.0",
        longitude="0.0",
    ):

        if category not in categories:
            return Promise.reject(
                GraphQLError('Invalid Category! Try with:' + ",".join(categories))
            )
        if stage not in stages:
            return Promise.reject(
                GraphQLError('Invalid Stage! Try with:' + ",".join(stages))
            )

        user = UserModel.query.get(user_id)

        project = ProjectModel(
            name=name,
            description=description,
            goal=goal,
            owner=user,
            category=category,
            stage=stage,
            latitude=latitude,
            longitude=longitude,
        )
        db.session.add(project)
        db.session.commit()

        id_project = project.id
        for h in hashtags:
            hashtag_model = HashtagModel(hashtag=h, id_project=id_project)
            db.session.add(hashtag_model)
        db.session.commit()

        return ProjectMutation(project=project)


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
