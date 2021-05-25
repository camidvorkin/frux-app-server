import graphene
import sqlalchemy
from graphql import GraphQLError
from promise import Promise

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db

from .constants import Category, Stage, State, categories, stages
from .object import Admin, Project, User
from .utils import is_valid_email, requires_auth


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        name = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    def mutate(self, info, name, email):  # pylint: disable=unused-argument

        if not is_valid_email(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        user = UserModel(name=name, email=email)

        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return Promise.reject(GraphQLError('Email address already registered!'))

        return UserMutation(user=user)


class AdminMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        user_id = graphene.String(required=True)

    admin = graphene.Field(lambda: Admin)

    def mutate(self, token, email, user_id):

        admin = AdminModel(token=token, email=email, user_id=user_id)

        db.session.add(admin)
        db.session.commit()

        return AdminMutation(admin=admin)


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

    project = graphene.Field(lambda: Project)

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

        return ProjectMutation(project=project)


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()
    mutate_admin = AdminMutation.Field()
