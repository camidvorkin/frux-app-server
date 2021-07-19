import graphene
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.object import Review
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.graphqlschema.validations import has_already_invest
from frux_app_server.models import Review as ReviewModel
from frux_app_server.models import db

from .project import get_project, is_project_invalid


class ReviewProjectMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        score = graphene.Float(required=True)
        description = graphene.String()

    Output = Review

    @requires_auth
    def mutate(
        self, info, id_project, score, description=None
    ):  # pylint: disable=unused-argument

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)

        if not has_already_invest(id_project, info.context.user.id):
            return Promise.reject(
                GraphQLError('Only investors of the project can add reviews!')
            )

        user_review = (
            db.session.query(ReviewModel)
            .filter_by(project_id=id_project, user_id=info.context.user.id)
            .first()
        )
        if not user_review:
            user_review = ReviewModel(score=score, description=description)
            project.reviews.append(user_review)
            info.context.user.reviews.append(user_review)
            db.session.add(user_review)
        else:
            user_review.score = score
            user_review.description = description

        db.session.commit()

        return user_review
