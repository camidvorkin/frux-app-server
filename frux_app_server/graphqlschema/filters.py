from math import pi

import graphene
import sqlalchemy
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet
from sqlalchemy import Float, cast
from sqlalchemy.sql import func

from frux_app_server.models import AssociationHashtag as AssociationHashtagModel
from frux_app_server.models import Investments as InvestmentsModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel

KM_PER_LAT = 2 * pi * 6371.009 / 360.0
DISTANCE = 10.0


class UserFilter(FilterSet):
    is_seeder = graphene.Boolean()
    is_sponsor = graphene.Boolean()

    class Meta:
        model = UserModel
        fields = {
            'username': [...],
            'email': [...],
            'is_seer': ['eq'],
            'is_blocked': ['eq'],
        }

    @classmethod
    def is_seeder_filter(self, info, query, value):  # pylint: disable=unused-argument

        project = self.aliased(query, ProjectModel, name='project_seer_association')

        query = query.outerjoin(
            project, sqlalchemy.and_(UserModel.id == project.user_id),
        )

        if value:
            filter_ = project.id.isnot(None)
        else:
            filter_ = project.id.is_(None)

        return query, filter_

    @classmethod
    def is_sponsor_filter(self, info, query, value):  # pylint: disable=unused-argument

        investment = self.aliased(query, InvestmentsModel, name='sponsor_association')

        query = query.outerjoin(
            investment, sqlalchemy.and_(UserModel.id == investment.user_id),
        )

        if value:
            filter_ = investment.project_id.isnot(None)
        else:
            filter_ = investment.project_id.is_(None)

        return query, filter_


class ProjectFilter(FilterSet):
    has_hashtag = graphene.List(graphene.String)
    is_closer_than = graphene.List(graphene.Float)

    class Meta:
        model = ProjectModel
        fields = {
            'name': [...],
            'description': [...],
            'category_name': [...],
            'current_state': [...],
            'is_blocked': ['eq'],
        }

    @classmethod
    def has_hashtag_filter(
        self, info, query, hashtags
    ):  # pylint: disable=unused-argument
        hashtag_association = self.aliased(query, AssociationHashtagModel)

        query = query.join(
            hashtag_association,
            sqlalchemy.and_(ProjectModel.id == hashtag_association.project_id,),
        )
        filter_ = hashtag_association.hashtag.in_(hashtags)
        print(query, filter_, hashtags)
        return query, filter_

    @staticmethod
    def is_closer_than_filter(info, query, location):  # pylint: disable=unused-argument
        '''
        location = [latitude, longitude, distance (optional)]
        '''
        n = location[2] if len(location) == 3 else DISTANCE
        return (
            KM_PER_LAT
            * func.sqrt(
                func.pow(location[0] - cast(ProjectModel.latitude, Float), 2)
                + func.pow(location[1] - cast(ProjectModel.longitude, Float), 2)
            )
        ) < n


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {UserModel: UserFilter(), ProjectModel: ProjectFilter()}
