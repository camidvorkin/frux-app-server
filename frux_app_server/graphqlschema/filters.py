from math import pi

import graphene
import sqlalchemy
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet
from sqlalchemy import Float, cast
from sqlalchemy.sql import func

from frux_app_server.models import AssociationHashtag as AssociationHashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel

KM_PER_LAT = 2 * pi * 6371.009 / 360.0
DISTANCE = 10.0


class UserFilter(FilterSet):
    class Meta:
        model = UserModel
        fields = {
            'username': [...],
            'email': [...],
            'is_seer': [...],
            'is_blocked': [...],
        }


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
