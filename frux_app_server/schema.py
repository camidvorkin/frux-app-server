import graphene

from .graphqlschema.mutation import Mutation
from .graphqlschema.query import Query

# pylint: disable=unused-argument
schema = graphene.Schema(query=Query, mutation=Mutation)
