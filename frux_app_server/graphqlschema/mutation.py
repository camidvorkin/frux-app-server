import datetime
import json
import os

import graphene
import requests
import sqlalchemy
from graphql import GraphQLError
from promise import Promise
from sqlalchemy.sql import func

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
from frux_app_server.models import Wallet as WalletModel
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
    Wallet,
)
from .utils import is_valid_email, is_valid_location, requires_auth, wei_to_eth


class UserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        image_path = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        description = graphene.String()
        latitude = graphene.String(required=True)
        longitude = graphene.String(required=True)
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
            longitude=longitude,
            latitude=latitude,
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
        latitude = graphene.String()
        longitude = graphene.String()
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
        latitude=None,
        longitude=None,
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
        if latitude and longitude and is_valid_location(latitude, longitude):
            user.latitude = latitude
            user.longitude = longitude
        if interests is not None:
            user.interests = []
            for c in interests:
                if db.session.query(CategoryModel).filter_by(name=c).count() != 1:
                    return Promise.reject(GraphQLError('Invalid Category!'))
                else:
                    category = db.session.query(CategoryModel).filter_by(name=c).one()
                user.interests.append(category)
        if user.creation_date_time is None:
            user.creation_date_time = datetime.datetime.utcnow()
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


class BlockUserMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    def mutate(self, info, user_id):  # pylint: disable=unused-argument

        query = db.session.query(UserModel).filter_by(id=user_id)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No user found!'))
        user = query.first()
        user.is_blocked = True
        db.session.commit()
        return user


class UnBlockUserMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    def mutate(self, info, user_id):  # pylint: disable=unused-argument

        query = db.session.query(UserModel).filter_by(id=user_id)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No user found!'))
        user = query.first()
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
        project = ProjectModel.query.get(id_project)

        if user.id != project.user_id:
            return Promise.reject(
                GraphQLError('This user is not the owner of the project!')
            )

        if project.has_seer:
            return Promise.reject(GraphQLError('Project has a seer already!'))

        # If the project does not have at least one stage, is rejected
        if len(project.stages) < 1:
            return Promise.reject(GraphQLError('Project must have at least one stage!'))

        # If there are none seers in the system, is rejected
        if db.session.query(UserModel).filter_by(is_seer=True).count() == 0:
            return Promise.reject(
                GraphQLError('There are no seer availables in the system :(')
            )
        seer = (
            db.session.query(UserModel)
            .filter_by(is_seer=True)
            .order_by(func.random())
            .first()
        )

        # Create wallet to project
        stages_cost = []
        new_goal = 0
        for stage in project.stages:
            stages_cost.append(stage.goal)
            new_goal += stage.goal
        body = {
            "ownerId": user.wallet.internal_id,
            "reviewerId": seer.wallet.internal_id,
            "stagesCost": stages_cost,
        }
        try:
            r = requests.post(
                f"{os.environ.get('FRUX_SC_URL', 'http://localhost:3000')}/project",
                json=body,
            )
        except requests.ConnectionError:
            return Promise.reject(
                GraphQLError('Unable to request project! Payments service is down!')
            )
        if r.status_code != 200:
            return Promise.reject(
                GraphQLError(f'Unable to request wallet! {r.status_code} - {r.text}')
            )

        response_json = json.loads(r.content.decode())
        project.smart_contract_hash = response_json["txHash"]
        project.seer = seer
        project.has_seer = True
        project.goal = new_goal
        project.current_state = State.FUNDING
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
        goal = graphene.Int()
        hashtags = graphene.List(graphene.String)
        category = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()
        uri_image = graphene.String()
        deadline = graphene.String(required=True)

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        name,
        description,
        goal,
        deadline,
        hashtags=None,
        category=None,
        latitude="0.0",
        longitude="0.0",
        current_state=(State.CREATED.value),
        uri_image="",
    ):  # pylint: disable=unused-argument
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

        deadline = deadline.split("-")
        deadline = datetime.datetime(
            int(deadline[0]), int(deadline[1]), int(deadline[2])
        )

        project = ProjectModel(
            name=name,
            description=description,
            goal=0,
            owner=info.context.user,
            category_name=category,
            latitude=latitude,
            longitude=longitude,
            deadline=deadline,
            creation_date=datetime.datetime.utcnow(),
            current_state=State.CREATED,
            uri_image=uri_image,
            has_seer=False,
            is_blocked=False,
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
        deadline = graphene.String()

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
        deadline=None,
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
            project.category_name = category

        if latitude and longitude and is_valid_location(latitude, longitude):
            project.latitude = latitude
            project.longitude = longitude
        if uri_image:
            project.uri_image = uri_image
        if deadline:
            project.deadline = deadline

        db.session.commit()
        return project


class InvestProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        invested_amount = graphene.Float(required=True)

    Output = Investments

    @requires_auth
    def mutate(self, info, id_project, invested_amount):

        query = db.session.query(ProjectModel).filter_by(id=id_project)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No project found!'))
        project = query.first()

        if project.current_state != State.FUNDING:
            return Promise.reject(GraphQLError('The project is not in funding state!'))

        if not info.context.user.wallet:
            return Promise.reject(GraphQLError('User does not have a wallet!'))

        body = {
            "funderId": info.context.user.wallet.internal_id,
            "amountToFund": invested_amount,
        }

        try:
            r = requests.post(
                f"{os.environ.get('FRUX_SC_URL', 'http://localhost:3000')}/project/{project.smart_contract_hash}",
                json=body,
            )
        except requests.ConnectionError:
            return Promise.reject(
                GraphQLError('Unable to request project! Payments service is down!')
            )

        if r.status_code != 200:
            error = json.loads(r.text)
            if error['code'] == 'INSUFFICIENT_FUNDS':
                return Promise.reject(
                    GraphQLError('Unable to fund project! Insufficient funds!')
                )
            return Promise.reject(
                GraphQLError(f'Unable to fund project! {r.status_code} - {r.text}')
            )

        tx = json.loads(r.text)
        invested_amount = wei_to_eth(tx['value']['hex'])

        project_collected = (
            db.session.query(func.sum(InvestmentsModel.invested_amount))
            .filter(InvestmentsModel.project_id == id_project)
            .scalar()
        )
        if project.goal - project_collected <= invested_amount:
            project.current_state = State.IN_PROGRESS
            invested_amount = project.goal - project_collected

        q = InvestmentsModel.query.filter_by(
            user_id=info.context.user.id, project_id=id_project
        )
        if q.count() == 0:
            invest = InvestmentsModel(
                user_id=info.context.user.id,
                project_id=id_project,
                invested_amount=invested_amount,
                date_of_investment=datetime.datetime.utcnow(),
            )
            db.session.add(invest)
        else:
            invest = q.first()
            invest.invested_amount += invested_amount
            invest.date_of_investment = datetime.datetime.utcnow()

        db.session.commit()
        return invest


class BlockProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    def mutate(
        self, info, id_project,
    ):  # pylint: disable=unused-argument

        query = db.session.query(ProjectModel).filter_by(id=id_project)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No project found!'))
        project = query.first()

        project.is_blocked = True
        db.session.commit()
        return project


class UnBlockProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    def mutate(
        self, info, id_project,
    ):  # pylint: disable=unused-argument

        query = db.session.query(ProjectModel).filter_by(id=id_project)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No project found!'))
        project = query.first()

        project.is_blocked = False
        db.session.commit()
        return project


class WithdrawFundsMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        withdraw_amount = graphene.Float(required=False)

    Output = Investments

    @requires_auth
    def mutate(self, info, id_project, withdraw_amount=None):

        query = db.session.query(ProjectModel).filter_by(id=id_project)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No project found!'))
        project = query.first()

        if (
            project.current_state != State.FUNDING
            and project.current_state != State.CANCELED
        ):
            return Promise.reject(
                GraphQLError('The project is not cancelled or in funding state!')
            )

        if not info.context.user.wallet:
            return Promise.reject(GraphQLError('User does not have a wallet!'))

        q = InvestmentsModel.query.filter_by(
            user_id=info.context.user.id, project_id=id_project
        )
        if q.count() == 0:
            return Promise.reject(GraphQLError('User did not invest in the project!'))

        investment = q.first()

        body = {'funderId': info.context.user.wallet.internal_id}

        if withdraw_amount:
            body['fundsToWithdraw'] = withdraw_amount
            if withdraw_amount > investment.invested_amount:
                return Promise.reject(GraphQLError('Invalid withdrawal amount!'))
        else:
            withdraw_amount = investment.invested_amount

        try:
            r = requests.post(
                f"{os.environ.get('FRUX_SC_URL', 'http://localhost:3000')}/project/{project.smart_contract_hash}/withdraw",
                json=body,
            )
        except requests.ConnectionError:
            return Promise.reject(
                GraphQLError('Unable to request project! Payments service is down!')
            )

        if r.status_code != 200:
            return Promise.reject(
                GraphQLError(f'Unable to withdraw! {r.status_code} - {r.text}')
            )

        investment.invested_amount -= withdraw_amount
        db.session.commit()

        return investment


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

        query = db.session.query(ProjectModel).filter_by(id=id_project)
        if query.count() != 1:
            return Promise.reject(GraphQLError('No project found!'))
        project = query.first()

        if info.context.user != project.owner:
            return Promise.reject(GraphQLError('User is not the project owner!'))

        stage = ProjectStageModel(
            title=title, project_id=id_project, description=description, goal=goal,
        )

        project = ProjectModel.query.get(id_project)
        project.stages.append(stage)

        new_goal = 0
        for stage in project.stages:
            new_goal += stage.goal

        project.goal = new_goal

        db.session.add(stage)
        db.session.commit()
        return stage


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    mutate_project = ProjectMutation.Field()
    mutate_admin = AdminMutation.Field()
    mutate_update_user = UpdateUser.Field()
    mutate_set_seer = SetSeerMutation.Field()
    mutate_block_user = BlockUserMutation.Field()
    mutate_unblock_user = UnBlockUserMutation.Field()
    mutate_update_project = UpdateProject.Field()
    mutate_invest_project = InvestProject.Field()
    mutate_seer_project = SeerProjectMutation.Field()
    mutate_block_project = BlockProjectMutation.Field()
    mutate_unblock_project = UnBlockProjectMutation.Field()
    mutate_fav_project = FavProject.Field()
    mutate_unfav_project = UnFavProject.Field()
    mutate_project_stage = ProjectStageMutation.Field()
    mutate_withdraw_funds = WithdrawFundsMutation.Field()
