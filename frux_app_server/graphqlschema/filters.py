from graphene_sqlalchemy_filter import FilterableConnectionField, FilterSet

from frux_app_server.models import User as UserModel


class UserFilter(FilterSet):
    class Meta:
        model = UserModel
        fields = {
            'name': ['eq', 'ne', 'in', 'ilike'],
            'email': ['eq', 'ne', 'in', 'ilike'],
        }


class FruxFilterableConnectionField(FilterableConnectionField):
    filters = {UserModel: UserFilter()}
