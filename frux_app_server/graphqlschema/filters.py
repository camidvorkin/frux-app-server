from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

from frux_app_server.models import Project as ProjectModel
from frux_app_server.models import User as UserModel


class UserFilter(FilterSet):
    class Meta:
        model = UserModel
        fields = {
            'name': ['eq', 'ne', 'in', 'ilike'],
            'email': ['eq', 'ne', 'in', 'ilike'],
        }


class ProjectFilter(FilterSet):
    class Meta:
        model = ProjectModel
        fields = {
            'name': ['eq', 'ne', 'in', 'ilike'],
            'description': ['eq', 'ne', 'in', 'ilike'],
            'category': ['eq', 'ne', 'in', 'ilike'],
        }


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {
        # UserModel: UserFilter(),
        ProjectModel: ProjectFilter()
    }
