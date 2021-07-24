import datetime

import graphene
import sqlalchemy
from graphql import GraphQLError
from promise import Promise

from frux_app_server.graphqlschema.object import User
from frux_app_server.graphqlschema.utils import get_category, requires_auth
from frux_app_server.graphqlschema.validations import (
    is_category_invalid,
    is_email_valid,
    is_location_valid,
)
from frux_app_server.models import User as UserModel
from frux_app_server.models import db
from frux_app_server.services import datadog_client

from .project import asign_seer, validate_seer_projects


def get_user(user_id):
    return db.session.query(UserModel).filter_by(id=user_id).one()


def is_user_invalid(user_id):
    return db.session.query(UserModel).filter_by(id=user_id).count() != 1


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
        if not is_email_valid(email):
            return Promise.reject(GraphQLError('Invalid email address!'))

        if not is_location_valid(latitude, longitude):
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
            if is_category_invalid(category):
                return Promise.reject(GraphQLError('Invalid Category!'))
            interest_category = get_category(category)
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
        if latitude and longitude and is_location_valid(latitude, longitude):
            user.latitude = latitude
            user.longitude = longitude
        if interests is not None:
            user.interests = []
            for c in set(interests):
                if is_category_invalid(c):
                    return Promise.reject(GraphQLError('Invalid Category!'))
                else:
                    category = get_category(c)
                user.interests.append(category)
        if user.creation_date_time is None:
            user.creation_date_time = datetime.datetime.utcnow()
        db.session.commit()
        return user


class BlockUserMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    def mutate(self, info, user_id):  # pylint: disable=unused-argument

        if is_user_invalid(user_id):
            return Promise.reject(GraphQLError('Not user found!'))
        user = get_user(user_id)
        user.is_blocked = True
        db.session.commit()
        datadog_client.new_blocked_user()
        return user


class UnBlockUserMutation(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    Output = User

    def mutate(self, info, user_id):  # pylint: disable=unused-argument
        if is_user_invalid(user_id):
            return Promise.reject(GraphQLError('Not user found!'))
        user = get_user(user_id)
        user.is_blocked = False
        db.session.commit()
        datadog_client.new_unblocked_user()
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


class RemoveSeerMutation(graphene.Mutation):
    Output = User

    @requires_auth
    def mutate(
        self, info,
    ):  # pylint: disable=unused-argument
        user = info.context.user

        if not validate_seer_projects(user.id):
            return Promise.reject(
                GraphQLError(
                    'Seer must wait until all their projects are either completed or cancelled! You can\'t leave the job in funding state'
                )
            )

        user.is_seer = False
        db.session.commit()

        asign_seer(user.id)
        return user
