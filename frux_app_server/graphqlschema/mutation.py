import datetime

import graphene
import sqlalchemy
from graphql import GraphQLError
from promise import Promise

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import (
    AssociationHashtag as AssociationHashtagModel,  # pylint: disable=unused-import
)
from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import Favorites as FavoritesModel
from frux_app_server.models import Hashtag as HashtagModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db

from .constants import State, states
from .object import (
    Admin,
    AssociationHashtag,
    Favorites,
    Investments,
    Project,
    ProjectStage,
    User,
)
from .utils import is_valid_email, is_valid_location, requires_auth


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        image_path = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        description = graphene.String()
        address = graphene.String()
        latitude = graphene.String(required=True)
        longitude = graphene.String(required=True)
        phone = graphene.String()
        interests = graphene.List(graphene.String)

    Output = User

    def mutate(
        self,
        info,
        username,
        email,
        image_path,
        first_name,
        last_name,
        latitude,
        longitude,
        description="",
        address="",
        phone="",
        interests=None,
    ):  # pylint: disable=unused-argument
        if not is_valid_email(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        if not is_valid_location(latitude, longitude):
            return Promise.reject(GraphQLError('Invalid location!'))

        if not interests:
            interests = []

        date = datetime.datetime.utcnow()
        user = UserModel(
            username=username,
            email=email,
            image_path=image_path,
            first_name=first_name,
            last_name=last_name,
            description=description,
            creation_date_time=date,
            last_login=date,
            address=address,
            longitude=longitude,
            latitude=latitude,
            phone=phone,
            is_seer=False,
            is_blocked=False,
        )

        for category in interests:
            if db.session.query(CategoryModel).filter_by(name=category).count() != 1:
                return Promise.reject(GraphQLError('Invalid Category!'))
            interest_category = (
                db.session.query(CategoryModel).filter_by(name=category).one()
            )
            user.interests.append(interest_category)

        db.session.add(user)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return Promise.reject(GraphQLError('Email address already registered!'))

        return user


class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        image_path = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        description = graphene.String()
        address = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()
        phone = graphene.String()
        interests = graphene.List(graphene.String)

    Output = User

    @requires_auth
    def mutate(
        self,
        info,
        username=None,
        image_path=None,
        first_name=None,
        last_name=None,
        description=None,
        address=None,
        latitude=None,
        longitude=None,
        phone=None,
        interests=None,
    ):  # pylint: disable=unused-argument
        user = info.context.user
        if username:
            user.username = username
        if image_path:
            user.image_path = image_path
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if description:
            user.description = description
        if address:
            user.address = address
        if latitude and longitude and is_valid_location(latitude, longitude):
            user.latitude = latitude
            user.longitude = longitude
        if phone:
            user.phone = phone
        if interests is not None:
            user.interests = []
            for c in interests:
                if db.session.query(CategoryModel).filter_by(name=c).count() != 1:
                    return Promise.reject(GraphQLError('Invalid Category!'))
                else:
                    category = db.session.query(CategoryModel).filter_by(name=c).one()
                user.interests.append(category)
        db.session.commit()
        return user


class SetSeerMutation(graphene.Mutation):
    Output = User

    @requires_auth
    def mutate(
        self, info,
    ):  # pylint: disable=unused-argument
        user = info.context.user
        user.is_seer = True
        db.session.commit()
        return user


class BlockedUserMutation(graphene.Mutation):

    Output = User

    @requires_auth
    def mutate(
        self, info,
    ):  # pylint: disable=unused-argument

        user = info.context.user
        user.is_blocked = True
        db.session.commit()
        return user


class UnblockedUserMutation(graphene.Mutation):

    Output = User

    @requires_auth
    def mutate(
        self, info,
    ):  # pylint: disable=unused-argument

        user = info.context.user
        user.is_blocked = False
        db.session.commit()
        return user


class SeerProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    @requires_auth
    def mutate(
        self, info, id_project,
    ):  # pylint: disable=unused-argument
        user = info.context.user
        if not user.is_seer:
            return Promise.reject(
                GraphQLError('This user does not have seer privilages!')
            )

        project = ProjectModel.query.get(id_project)
        if project.has_seer:
            return Promise.reject(GraphQLError('Project has a seer already!'))

        user.seer_projects.append(project)
        project.has_seer = True
        db.session.commit()
        return project


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
        latitude = graphene.String()
        longitude = graphene.String()
        uri_image = graphene.String()

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        name,
        description,
        goal,
        hashtags=None,
        category=None,
        latitude="0.0",
        longitude="0.0",
        current_state=(State.CREATED.value),
        uri_image="",
    ):
        if not hashtags:
            hashtags = []

        if (
            category
            and db.session.query(CategoryModel).filter_by(name=category).count() != 1
        ):
            return Promise.reject(GraphQLError('Invalid Category!'))

        if current_state not in states:
            return Promise.reject(
                GraphQLError('Invalid Stage! Try with:' + ",".join(states))
            )

        project = ProjectModel(
            name=name,
            description=description,
            goal=goal,
            owner=info.context.user,
            category_name=category,
            latitude=latitude,
            longitude=longitude,
            current_state=State.CREATED,
            uri_image=uri_image,
            has_seer=False,
        )
        db.session.add(project)

        for h in hashtags:
            if db.session.query(HashtagModel).filter_by(hashtag=h).count() != 1:
                hashtag = HashtagModel(hashtag=h)
                db.session.add(hashtag)

            association = AssociationHashtagModel(hashtag=h, project_id=project.id)
            db.session.add(association)

        db.session.commit()
        return project


class UpdateProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        name = graphene.String()
        description = graphene.String()
        hashtags = graphene.List(graphene.String)
        category = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()
        uri_image = graphene.String()

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        id_project,
        name=None,
        description=None,
        hashtags=None,
        category=None,
        latitude=None,
        longitude=None,
        uri_image=None,
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

        if hashtags is not None:
            db.session.query(AssociationHashtagModel).filter_by(
                project_id=id_project
            ).delete()
            for h in hashtags:
                if db.session.query(HashtagModel).filter_by(hashtag=h).count() != 1:
                    hashtag = HashtagModel(hashtag=h)
                    db.session.add(hashtag)

                association = AssociationHashtagModel(hashtag=h, project_id=project.id)
                db.session.add(association)

        if category is not None:
            if db.session.query(CategoryModel).filter_by(name=category).count() != 1:
                return Promise.reject(GraphQLError('Invalid Category!'))
            project.category = category

        if latitude and longitude and is_valid_location(latitude, longitude):
            project.latitude = latitude
            project.longitude = longitude
        if uri_image:
            project.uri_image = uri_image

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


class FavProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Favorites

    @requires_auth
    def mutate(self, info, id_project):

        fav = FavoritesModel(user_id=info.context.user.id, project_id=id_project,)

        try:
            db.session.add(fav)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            pass

        return fav


class UnFavProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Favorites

    @requires_auth
    def mutate(self, info, id_project):

        FavoritesModel.query.filter_by(
            user_id=info.context.user.id, project_id=id_project
        ).delete()
        db.session.commit()
        return FavoritesModel(user_id=info.context.user.id, project_id=id_project,)


class ProjectStageMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        goal = graphene.Float(required=True)

    Output = ProjectStage

    @requires_auth
    def mutate(
        self, info, id_project, title, description, goal
    ):  # pylint: disable=unused-argument

        stage = ProjectStageModel(
            title=title, project_id=id_project, description=description, goal=goal,
        )

        project = ProjectModel.query.get(id_project)
        project.stages.append(stage)

        db.session.add(stage)
        db.session.commit()
        return stage


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()
    mutate_admin = AdminMutation.Field()
    mutate_update_user = UpdateUser.Field()
    mutate_set_veer = SetSeerMutation.Field()
    mutate_set_to_blocked = BlockedUserMutation.Field()
    mutate_update_project = UpdateProject.Field()
    mutate_invest_project = InvestProject.Field()
    mutate_seer_project = SeerProjectMutation.Field()
    mutate_fav_project = FavProject.Field()
    mutate_unfav_project = UnFavProject.Field()
    mutate_project_stage = ProjectStageMutation.Field()
