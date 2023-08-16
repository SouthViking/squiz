import graphene

from users.schema import UserMutations
from users.queries.user import UsersQueries

from quizzes.schema import QuizMutations
from quizzes.queries.quiz import QuizQueries

class Queries(UsersQueries, QuizQueries, graphene.ObjectType):
    pass

class Mutations(UserMutations, QuizMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query = Queries, mutation = Mutations)