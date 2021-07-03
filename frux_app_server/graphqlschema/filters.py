from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

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
    class Meta:
        model = ProjectModel
        fields = {
            'name': [...],
            'description': [...],
            'category_name': [...],
        }


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {UserModel: UserFilter(), ProjectModel: ProjectFilter()}
