import json
import os
import re

import requests
import sqlalchemy
from firebase_admin import auth
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import GraphQLError
from promise import Promise

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import Wallet as WalletModel
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


def request_user_wallet(user):
    try:
        r = requests.post(
            f"{os.environ.get('FRUX_SC_URL', 'http://localhost:3000')}/wallet"
        )
    except requests.ConnectionError:
        return

    if r.status_code != 200:
        return

    response_json = json.loads(r.content.decode())
    wallet = WalletModel(
        internal_id=response_json["id"], address=response_json["address"]
    )

    db.session.add(wallet)
    user.wallet_address = wallet.address


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

        if not info.context.user.wallet_address:
            request_user_wallet(info.context.user)
            db.session.commit()

        return func(obj, info, **kwargs)

    return wrapper


def wei_to_eth(wei_hex):
    return float.fromhex(wei_hex) / (10 ** 18)


class CustomSQLAlchemyConnectionField(SQLAlchemyConnectionField):
    @classmethod
    def get_query(cls, model, info, sort=None, **args):
        return requires_auth(super(CustomSQLAlchemyConnectionField, cls).get_query)(
            model, info, sort=sort, **args
        )


def get_project(project_id):
    query = db.session.query(ProjectModel).filter_by(id=project_id)
    if query.count() != 1:
        return Promise.reject(GraphQLError('No project found!'))
    return query.first()
