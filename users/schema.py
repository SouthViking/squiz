import graphene

from .mutators import (
    TokenRefreshMutation,
    RegistrationMutation,
    EmailVerificationMutation,
    UserAuthenticationMutation,
    ResendEmailVerificationTokenMutation,
)

from .queries import (
    UsersQueries as InternalUserQueries
)

class UserMutations(graphene.ObjectType):
    registrate_user = RegistrationMutation.Field()
    resend_email_verification_token = ResendEmailVerificationTokenMutation.Field()
    verify_email = EmailVerificationMutation.Field()
    authenticate_user = UserAuthenticationMutation.Field()
    token_refresh = TokenRefreshMutation.Field()

class UserQueries(InternalUserQueries):
    pass