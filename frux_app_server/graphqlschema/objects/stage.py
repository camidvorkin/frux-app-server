import datetime

import graphene
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.object import ProjectStage
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import db

from .project import get_project, is_project_invalid


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
