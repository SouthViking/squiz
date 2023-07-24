import graphene

from users.schema import (
    RegistrationMutation,
)

class Queries(graphene.ObjectType):
    hello = graphene.String(default_value = 'Hi!')

class Mutations(graphene.ObjectType):
    registrate_user = RegistrationMutation.Field()

schema = graphene.Schema(query = Queries, mutation = Mutations)