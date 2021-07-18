import graphene
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.object import Admin
from frux_app_server.graphqlschema.validations import is_email_valid
from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import db


class AdminMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        user_id = graphene.String(required=True)

    Output = Admin
    admin = graphene.Field(lambda: Admin)

    def mutate(self, token, email, user_id):

        if not is_email_valid(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        admin = AdminModel(token=token, email=email, user_id=user_id)

        db.session.add(admin)
        db.session.commit()

        return admin
