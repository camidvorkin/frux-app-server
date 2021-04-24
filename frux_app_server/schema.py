# flask_sqlalchemy/schema.py
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from .models import Project as ProjectModel
from .models import User as UserModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node,)


class Project(SQLAlchemyObjectType):
    class Meta:
        model = ProjectModel
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_projects = SQLAlchemyConnectionField(Project.connection)
    # Disable sorting over this field
    all_users = SQLAlchemyConnectionField(User.connection, sort=None)


schema = graphene.Schema(query=Query)
