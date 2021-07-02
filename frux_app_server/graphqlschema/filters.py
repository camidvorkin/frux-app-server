import graphene
import sqlalchemy
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet
from sqlalchemy import Float, cast

from frux_app_server.models import AssociationHashtag as AssociationHashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel

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

    @classmethod
    def is_closer_than_filter(
        self, info, query, location
    ):  # pylint: disable=unused-argument
        '''
        location = [latitude, longitude, distance (optional)]
        '''
        project_location = self.aliased(query, ProjectModel)
        latitude = location[0]
        longitude = location[1]
        n = location[2] if len(location) == 3 else DISTANCE
        return sqlalchemy.and_(
            cast(project_location.latitude, Float) < latitude + n,
            cast(project_location.latitude, Float) > latitude - n,
            cast(project_location.longitude, Float) < longitude + n,
            cast(project_location.longitude, Float) > longitude - n,
        )


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {UserModel: UserFilter(), ProjectModel: ProjectFilter()}
