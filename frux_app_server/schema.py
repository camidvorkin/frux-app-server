import graphene

from .graphql.mutation import Mutation
from .graphql.query import Query

# pylint: disable=unused-argument
schema = graphene.Schema(query=Query, mutation=Mutation)
