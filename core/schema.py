import graphene

from users.schema import (
    RegistrationMutation,
    ResendEmailVerificationTokenMutation,
    EmailVerificationMutation,
    UserAuthenticationMutation,
    TokenRefreshMutation,
)

class Queries(graphene.ObjectType):
    hello = graphene.String(default_value = 'Hi!')

class Mutations(graphene.ObjectType):
    registrate_user = RegistrationMutation.Field()
    resend_email_verification_token = ResendEmailVerificationTokenMutation.Field()
    verify_email = EmailVerificationMutation.Field()
    authenticate_user = UserAuthenticationMutation.Field()
    token_refresh = TokenRefreshMutation.Field()

schema = graphene.Schema(query = Queries, mutation = Mutations)