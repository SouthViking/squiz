import graphene

from users.schema import (
    RegistrationMutation,
    ResendEmailVerificationTokenMutation,
    EmailVerificationMutation,
)

class Queries(graphene.ObjectType):
    hello = graphene.String(default_value = 'Hi!')

class Mutations(graphene.ObjectType):
    registrate_user = RegistrationMutation.Field()
    resend_email_verification_token = ResendEmailVerificationTokenMutation.Field()
    verify_email = EmailVerificationMutation.Field()

schema = graphene.Schema(query = Queries, mutation = Mutations)