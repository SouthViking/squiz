import graphene

from users.mutators import (
    RegistrationMutation,
    ResendEmailVerificationTokenMutation,
    EmailVerificationMutation,
    UserAuthenticationMutation,
    TokenRefreshMutation,
)

from quizzes.mutators import (
    QuizCreationMutation,
    QuizUpdateMutation,
    QuestionCreationMutation,
    QuestionUpdateMutation,
)

class Queries(graphene.ObjectType):
    bar = graphene.String(default_value = 'foo')

class Mutations(graphene.ObjectType):
    registrate_user = RegistrationMutation.Field()
    resend_email_verification_token = ResendEmailVerificationTokenMutation.Field()
    verify_email = EmailVerificationMutation.Field()
    authenticate_user = UserAuthenticationMutation.Field()
    token_refresh = TokenRefreshMutation.Field()

    create_quiz = QuizCreationMutation.Field()
    update_quiz = QuizUpdateMutation.Field()

    create_question = QuestionCreationMutation.Field()
    update_question = QuestionUpdateMutation.Field()

schema = graphene.Schema(query = Queries, mutation = Mutations)