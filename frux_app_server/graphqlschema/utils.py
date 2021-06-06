import re

import sqlalchemy
from firebase_admin import auth
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import GraphQLError

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import db


def is_valid_email(email):
    return re.match(
        r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
        email,
    )


def is_valid_location(latitude, longitude):
    return re.match(r"^(\-?([0-8]?[0-9](\.\d+)?|90(.[0]+)?))$", latitude) and re.match(
        r"^(\-?([1]?[0-7]?[0-9](\.\d+)?|180((.[0]+)?)))$", longitude
    )


def requires_auth(func):
    '''
    Authorization decorator for graphql queries/objects.
    Users are authenticated with a Bearer Token given by the firebase app.
    Once authenticated, finds the current user in the database and if
    it doesn't exists it creates it.
    Assigns the current user db object to `info.context.user`.
    '''

    def wrapper(obj, info, **kwargs):
        if 'Authorization' not in info.context.headers:
            raise GraphQLError('Missing Bearer token')
        try:
            token = info.context.headers['Authorization'].split()[-1]
            userinfo = AdminModel.query.get(token)
            if not userinfo:
                userinfo = auth.verify_id_token(token)
                user_email = userinfo['email']
            else:
                user_email = userinfo.email
        except auth.ExpiredIdTokenError as e:
            raise GraphQLError('Expired token error') from e
        except auth.InvalidIdTokenError as e:
            raise GraphQLError('Invalid Bearer token') from e
        except auth.TokenSignError as e:
            raise GraphQLError('Token sign error') from e

        try:
            info.context.user = (
                db.session.query(UserModel).filter_by(email=user_email).one()
            )
        except sqlalchemy.orm.exc.NoResultFound:
            info.context.user = UserModel(email=user_email)
            db.session.add(info.context.user)
            db.session.commit()
        return func(obj, info, **kwargs)

    return wrapper


class CustomSQLAlchemyConnectionField(SQLAlchemyConnectionField):
    @classmethod
    def get_query(cls, model, info, sort=None, **args):
        return requires_auth(super(CustomSQLAlchemyConnectionField, cls).get_query)(
            model, info, sort=sort, **args
        )
