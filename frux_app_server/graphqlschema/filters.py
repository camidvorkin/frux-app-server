import graphene
import sqlalchemy
from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

from frux_app_server.models import AssociationHashtag as AssociationHashtagModel
from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel


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
        return query, filter_


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {UserModel: UserFilter(), ProjectModel: ProjectFilter()}
