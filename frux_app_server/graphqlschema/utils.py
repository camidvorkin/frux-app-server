import time

import sqlalchemy
from firebase_admin import auth
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphql import GraphQLError
from sqlalchemy.sql import func

from frux_app_server.models import Admin as AdminModel
from frux_app_server.models import Category as CategoryModel
from frux_app_server.models import ProjectStage as ProjectStageModel
from frux_app_server.models import User as UserModel
from frux_app_server.models import Wallet as WalletModel
from frux_app_server.models import db
from frux_app_server.services import datadog_client
from frux_app_server.services.smart_contract_client import smart_contract_client


def request_user_wallet(user):
    response_json = smart_contract_client.create_user_wallet()
    if not response_json:
        return

    wallet = WalletModel(
        internal_id=response_json["id"], address=response_json["address"]
    )

    db.session.add(wallet)
    user.wallet_address = wallet.address


def requires_auth(function):
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
            provider = None
            if not userinfo:
                userinfo = auth.verify_id_token(token)
                user_email = userinfo['email']
                provider = userinfo['firebase']['sign_in_provider']
                auth_time = userinfo['auth_time']
                if time.time() - auth_time < 60:
                    datadog_client.new_login(provider)
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
            if provider:
                datadog_client.new_user(provider)

        if not info.context.user.wallet_address:
            request_user_wallet(info.context.user)
            db.session.commit()
        return function(obj, info, **kwargs)

    return wrapper


def wei_to_eth(wei_hex):
    return float.fromhex(wei_hex) / (10 ** 18)


class CustomSQLAlchemyConnectionField(SQLAlchemyConnectionField):
    @classmethod
    def get_query(cls, model, info, sort=None, **args):
        return requires_auth(super(CustomSQLAlchemyConnectionField, cls).get_query)(
            model, info, sort=sort, **args
        )


def get_category(category):
    return db.session.query(CategoryModel).filter_by(name=category).one()


def get_seer():
    return (
        db.session.query(UserModel)
        .filter_by(is_seer=True)
        .order_by(func.random())
        .first()
    )


def get_project_stage(id_project, id_stage):
    return (
        db.session.query(ProjectStageModel)
        .filter_by(project_id=id_project, stage_index=id_stage)
        .one()
    )
