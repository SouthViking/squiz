import graphene

from users.schema import UserMutations
from users.queries.user import UsersQueries

from quizzes.schema import QuizMutations

class Queries(UsersQueries, graphene.ObjectType):
    pass

class Mutations(UserMutations, QuizMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Queries, mutation = Mutations)