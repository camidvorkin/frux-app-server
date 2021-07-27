import datetime

import graphene
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.constants import State, states
from frux_app_server.graphqlschema.object import Project
from frux_app_server.graphqlschema.utils import (
    get_project_stage,
    get_seer,
    requires_auth,
)
from frux_app_server.graphqlschema.validations import (
    has_seer,
    is_category_invalid,
    is_location_valid,
)
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import db
from frux_app_server.services import datadog_client
from frux_app_server.services.chat_client import chat_client
from frux_app_server.services.smart_contract_client import smart_contract_client

from .hashtag import add_hashtags, delete_hashtags


def get_project(project_id):
    return db.session.query(ProjectModel).filter_by(id=project_id).one()


def is_project_invalid(project_id):
    return db.session.query(ProjectModel).filter_by(id=project_id).count() != 1


def asign_seer(user_id):
    projects = db.session.query(ProjectModel).filter_by(seer_id=user_id)
    for project in projects:
        project.has_seer = False
        seer = get_seer()
        if seer is not None:
            project.seer = seer
            project.has_seer = True
        db.session.commit()


def validate_seer_projects(user_id):
    # TODO: improve this cuz is horrible
    projects = db.session.query(ProjectModel).filter_by(seer_id=user_id)
    for project in projects:
        if project.current_state in [State.FUNDING, State.IN_PROGRESS]:
            return False
    return True


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

    class Meta:
        description = 'Adds a new project to the system'

    Output = Project

    @requires_auth
    def mutate(
        self,
        info,
        name,
        description,
        deadline,
        goal=0,
        hashtags=None,
        category=None,
        latitude="0.0",
        longitude="0.0",
        current_state=(State.CREATED.value),
        uri_image="",
    ):  # pylint: disable=unused-argument
        if not hashtags:
            hashtags = []

        if is_category_invalid(category):
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
        db.session.commit()
        add_hashtags(hashtags, project.id)

        datadog_client.set_project_in_state(project.current_state.value)
        datadog_client.set_project_in_category(project.category_name)

        chat_client.subscribe_project_creator(project.id, info.context.user.id)

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
        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)
        if info.context.user != project.owner:
            return Promise.reject(
                GraphQLError('Invalid ownership. This user cannot modify this project')
            )

        if name:
            project.name = name
        if description:
            project.description = description

        if hashtags is not None:
            delete_hashtags(id_project)
            add_hashtags(hashtags, id_project)

        if category is not None:
            if is_category_invalid(category):
                return Promise.reject(GraphQLError('Invalid Category!'))
            project.category_name = category

        if latitude and longitude and is_location_valid(latitude, longitude):
            project.latitude = latitude
            project.longitude = longitude
        if uri_image:
            project.uri_image = uri_image
        if deadline:
            project.deadline = deadline

        db.session.commit()

        datadog_client.set_project_in_state(project.current_state.value)
        datadog_client.set_project_in_category(project.category_name)

        return project


class BlockProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    def mutate(
        self, info, id_project,
    ):  # pylint: disable=unused-argument

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)
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

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)
        project.is_blocked = False
        db.session.commit()
        return project


class CompleteStageMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        id_stage = graphene.Int()

    Output = Project

    @requires_auth
    def mutate(
        self, info, id_project, id_stage=None
    ):  # pylint: disable=unused-argument

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)
        if project.seer.id != info.context.user.id:
            return Promise.reject(
                GraphQLError('This user is not the seer of the project!')
            )

        max_stage = len(project.stages)
        if id_stage is None or id_stage > max_stage:
            id_stage = max_stage

        stage = get_project_stage(id_project, id_stage)
        if stage.funds_released:
            return Promise.reject(GraphQLError('This stage was already released!'))

        stage_index = stage.stage_index

        smart_contract_client.complete_stage(
            info.context.user.wallet.internal_id,
            project.smart_contract_hash,
            stage_index,
        )

        for stage in sorted(project.stages, key=lambda x: x.creation_date):
            if stage.stage_index > stage_index:
                break
            stage.funds_released = True
            stage.fund_released_at = datetime.datetime.utcnow()
        if id_stage == max_stage:
            project.current_state = State.COMPLETE
            chat_client.notify_change_state(project)

        db.session.commit()
        datadog_client.set_project_in_state(project.current_state.value)
        chat_client.notify_new_stage(project, stage, info.context.user)
        return project


class SeerProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    @requires_auth
    def mutate(
        self, info, id_project,
    ):  # pylint: disable=unused-argument
        user = info.context.user
        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)

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
        if not has_seer():
            return Promise.reject(
                GraphQLError('There are no seer availables in the system :(')
            )
        seer = get_seer()

        # Create wallet to project
        stages_cost = []
        new_goal = 0
        for index, stage in enumerate(
            sorted(project.stages, key=lambda x: x.creation_date), 1
        ):
            stage.stage_index = index
            stages_cost.append(stage.goal)
            new_goal += stage.goal

        tx_hash = smart_contract_client.create_project_smart_contract(
            user.wallet.internal_id, seer.wallet.internal_id, stages_cost,
        )

        project.smart_contract_hash = tx_hash
        project.seer = seer
        project.has_seer = True
        project.goal = new_goal
        project.current_state = State.FUNDING
        db.session.commit()

        datadog_client.set_project_in_state(project.current_state.value)
        chat_client.subscribe_project_seer(project.id, info.context.user.id)
        chat_client.notify_new_seer(project, info.context.user)
        chat_client.notify_change_state(project)

        return project


class CancelProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)

    Output = Project

    @requires_auth
    def mutate(self, info, id_project):  # pylint: disable=unused-argument

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)

        user_email = info.context.user.email
        if project.owner.email != user_email and (
            project.seer is not None and project.seer.email != user_email
        ):
            return Promise.reject(
                GraphQLError('This user is not the owner of the project!')
            )

        project.current_state = State.CANCELED
        db.session.commit()
        return project
