import datetime

import graphene
import sqlalchemy
from graphql import GraphQLError
from promise import Promise

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db

from .constants import Category, Stage, State, categories, stages
from .object import Admin, Investments, Project, User
from .utils import is_valid_email, requires_auth


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)

    Output = User

    def mutate(self, info, name, email):  # pylint: disable=unused-argument

        if not is_valid_email(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        user = UserModel(name=name, email=email)

        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return Promise.reject(GraphQLError('Email address already registered!'))

        return user


class UpdateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        name = graphene.String()

    Output = User

    @requires_auth
    def mutate(self, info, name=None, email=None):  # pylint: disable=unused-argument
        user = info.context.user
        if name:
            user.name = name
        if email:
            if not is_valid_email(email):
                return Promise.reject(GraphQLError('Invalid email address!'))
            user.email = email
        db.session.commit()
        return user


class AdminMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        user_id = graphene.String(required=True)

    Output = Admin
    admin = graphene.Field(lambda: Admin)

    def mutate(self, token, email, user_id):

        admin = AdminModel(token=token, email=email, user_id=user_id)

        db.session.add(admin)
        db.session.commit()

        return admin


class ProjectMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        goal = graphene.Int(required=True)
        hashtags = graphene.List(graphene.String)
        category = graphene.String()
        stage = graphene.String()
        stage_goal = graphene.Int()
        stage_description = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        name,
        description,
        goal,
        hashtags=None,
        category=(Category.OTHERS.value),
        stage=(Stage.IN_PROGRESS.value),
        stage_goal=0,
        stage_description="",
        latitude="0.0",
        longitude="0.0",
    ):
        if not hashtags:
            hashtags = []

        if category not in categories:
            return Promise.reject(
                GraphQLError('Invalid Category! Try with:' + ",".join(categories))
            )
        if stage not in stages:
            return Promise.reject(
                GraphQLError('Invalid Stage! Try with:' + ",".join(stages))
            )

        project_stage = ProjectStageModel(
            stage=stage, goal=stage_goal, description=stage_description
        )
        db.session.add(project_stage)

        project = ProjectModel(
            name=name,
            description=description,
            goal=goal,
            owner=info.context.user,
            stage=project_stage,
            category=category,
            latitude=latitude,
            longitude=longitude,
            current_state=State.CREATED,
        )
        db.session.add(project)
        db.session.commit()

        id_project = project.id
        for h in hashtags:
            hashtag_model = HashtagModel(hashtag=h, id_project=id_project)
            db.session.add(hashtag_model)
            db.session.commit()

        return project


class UpdateProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        goal = graphene.Int()
        hashtags = graphene.List(graphene.String)
        category = graphene.String()
        stage = graphene.String()
        stage_goal = graphene.Int()
        stage_description = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        id_project,
        name=None,
        description=None,
        goal=None,
        hashtags=None,
        category=None,
        stage_description=None,
    ):

        project = ProjectModel.query.get(id_project)
        if info.context.user != project.owner:
            return Promise.reject(
                GraphQLError('Invalid ownership. This user cannot modify this project')
            )

        if name:
            project.name = name
        if description:
            project.description = description
        if goal:
            project.goal = goal
        if hashtags:
            id_project = project.id
            for h in hashtags:
                hashtag_model = HashtagModel(hashtag=h, id_project=id_project)
                db.session.add(hashtag_model)
                db.session.commit()
        if category:
            if category not in categories:
                return Promise.reject(
                    GraphQLError('Invalid Category! Try with:' + ",".join(categories))
                )
            project.category = category
        if stage_description:
            project.stage_description = stage_description

        db.session.commit()
        return project


class InvestProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        invested_amount = graphene.Float(required=True)

    Output = Investments

    @requires_auth
    def mutate(self, info, id_project, invested_amount):

        invest = InvestmentsModel(
            user_id=info.context.user.id,
            project_id=id_project,
            invested_amount=invested_amount,
            date_of_investment=datetime.datetime.utcnow(),
        )

        db.session.add(invest)
        db.session.commit()
        return invest


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()
    mutate_admin = AdminMutation.Field()
    mutate_update_user = UpdateUser.Field()
    mutate_update_project = UpdateProject.Field()
    mutate_invest_project = InvestProject.Field()
