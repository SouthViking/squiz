import graphene

from users.schema import UserMutations, UserQueries
from quizzes.schema import QuizMutations, QuizQueries

class Queries(UserQueries, QuizQueries, graphene.ObjectType):
    pass

class Mutations(UserMutations, QuizMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Queries, mutation = Mutations)