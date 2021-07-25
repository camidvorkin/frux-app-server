import datetime

import graphene
from graphql import GraphQLError
from promise import Promise
from sqlalchemy.sql import func

from frux_app_server.graphqlschema.constants import State
from frux_app_server.graphqlschema.object import Investments
from frux_app_server.graphqlschema.utils import requires_auth
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import db
from frux_app_server.services import datadog_client
from frux_app_server.services.smart_contract_client import smart_contract_client

from .project import get_project, is_project_invalid


def get_investment(user_id, project_id):
    return InvestmentsModel.query.filter_by(user_id=user_id, project_id=project_id)


class InvestProject(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        invested_amount = graphene.Float(required=True)

    Output = Investments

    @requires_auth
    def mutate(self, info, id_project, invested_amount):

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)

        if project.current_state != State.FUNDING:
            return Promise.reject(GraphQLError('The project is not in funding state!'))

        if not info.context.user.wallet:
            return Promise.reject(GraphQLError('User does not have a wallet!'))

        invested_amount = smart_contract_client.invest_project(
            project.smart_contract_hash,
            info.context.user.wallet.internal_id,
            invested_amount,
        )

        # Sum all the invesments for the project
        project_collected = (
            db.session.query(func.sum(InvestmentsModel.invested_amount))
            .filter(InvestmentsModel.project_id == id_project)
            .scalar()
        )
        if not project_collected:
            project_collected = 0

        # If the new investment is more than the rest to collect
        if project.goal - project_collected <= invested_amount:
            project.current_state = State.IN_PROGRESS
            invested_amount = project.goal - project_collected
            first_stage = sorted(project.stages, key=lambda x: x.stage_index)[0]
            first_stage.funds_released = True

        q = get_investment(info.context.user.id, id_project)
        # If user hasn't already invest, an invest is add to the InvestmentsModel, else the amount invested is sum up
        if q.count() == 0:
            invest = InvestmentsModel(
                user_id=info.context.user.id,
                project_id=id_project,
                invested_amount=invested_amount,
                date_of_investment=datetime.datetime.today(),
            )
            db.session.add(invest)
        else:
            invest = q.first()
            invest.invested_amount += invested_amount
            invest.date_of_investment = datetime.datetime.today()

        db.session.commit()
        datadog_client.set_project_in_state(project.current_state)
        return invest


class WithdrawFundsMutation(graphene.Mutation):
    class Arguments:
        id_project = graphene.Int(required=True)
        withdraw_amount = graphene.Float(required=False)

    Output = Investments

    @requires_auth
    def mutate(self, info, id_project, withdraw_amount=None):

        if is_project_invalid(id_project):
            return Promise.reject(GraphQLError('Not project found!'))
        project = get_project(id_project)
        if (
            project.current_state != State.FUNDING
            and project.current_state != State.CANCELED
        ):
            return Promise.reject(
                GraphQLError('The project is not cancelled or in funding state!')
            )

        if not info.context.user.wallet:
            return Promise.reject(GraphQLError('User does not have a wallet!'))

        q = get_investment(info.context.user.id, id_project)
        if q.count() == 0:
            return Promise.reject(GraphQLError('User did not invest in the project!'))

        investment = q.first()

        if not withdraw_amount:
            withdraw_amount = investment.invested_amount
        elif withdraw_amount > investment.invested_amount:
            return Promise.reject(GraphQLError('Invalid withdrawal amount!'))

        smart_contract_client.withdraw_funds(
            project.smart_contract_hash,
            info.context.user.wallet.internal_id,
            withdraw_amount,
        )

        investment.invested_amount -= withdraw_amount
        db.session.commit()

        return investment
