import datetime

import graphene
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.constants import State
from frux_app_server.graphqlschema.object import ProjectStage
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import db

from .project import get_project, is_project_invalid


def validate_project(user, project_id):
    if is_project_invalid(project_id):
        raise GraphQLError('Not project found!')
    project = get_project(project_id)

    if user != project.owner:
        raise GraphQLError('User is not the project owner!')

    if project.current_state != State.CREATED:
        raise GraphQLError('User can\'t modify the stages past the CREATION state')


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

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)

        if info.context.user != project.owner:
            return Promise.reject(GraphQLError('User is not the project owner!'))

        stage = ProjectStageModel(
            title=title,
            project_id=id_project,
            description=description,
            goal=goal,
            creation_date=datetime.datetime.today(),
        )
        project.stages.append(stage)
        project.goal += stage.goal

        db.session.add(stage)
        db.session.commit()
        return stage


class UpdateProjectStageMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        id_stage = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        goal = graphene.Float()

    Output = ProjectStage

    @requires_auth
    def mutate(
        self, info, id_project, id_stage, title=None, description=None, goal=None
    ):  # pylint: disable=unused-argument

        validate_project(info.context.user, id_project)

        stage = ProjectStageModel.query.get(id_stage)
        if stage is None:
            return Promise.reject(
                GraphQLError(f'There is no stage {id_stage} for this project')
            )

        if title is not None:
            stage.title = title
        if description is not None:
            stage.description = description
        if goal is not None:
            stage.goal = goal

        db.session.commit()
        return stage


class RemoveProjectStageMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        id_stage = graphene.Int(required=True)

    Output = ProjectStage

    @requires_auth
    def mutate(self, info, id_project, id_stage):  # pylint: disable=unused-argument

        validate_project(info.context.user, id_project)

        stage = ProjectStageModel.query.get(id_stage)
        if stage is None:
            return Promise.reject(
                GraphQLError(f'There is no stage {id_stage} for this project')
            )
        db.session.delete(stage)
        db.session.commit()
        return stage
