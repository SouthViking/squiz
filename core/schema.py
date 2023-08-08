import graphene

from users.schema import UserMutations
from quizzes.schema import QuizMutations

class Queries(graphene.ObjectType):
    bar = graphene.String(default_value = 'foo')

class Mutations(UserMutations, QuizMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Queries, mutation = Mutations)