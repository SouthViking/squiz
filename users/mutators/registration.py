import graphene
from django.core.validators import validate_email

from users.models import User
from core.decorators import tryable_mutation
from core.graphene.common import BaseMutationResult
from users.utils import generate_and_send_email_verification_token

class RegistrationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        full_name = graphene.String(required = True)
        nickname = graphene.String(required = True)
        email = graphene.String(required = True)
        password = graphene.String(required = True)

    class Meta:
        description = 'Executes the process to register a new user in the platform.'

    @tryable_mutation(required_fields = ['full_name', 'nickname', 'email', 'password'])
    def mutate(root, info, **data):
        user_record_count = User.objects.filter(email = data['email']).count()
        if user_record_count > 0:
            return {
                'success': False,
                'message': f'A user with email {data["email"]} has already been registered in the platform.',
            }
        
        validate_email(data['email'])
        
        User.objects.create(
            full_name = data['full_name'],
            nickname = data['nickname'],
            email = data['email'],
            password = data['password'],
        )

        generate_and_send_email_verification_token(data['email'])

        return {
            'success': True,
            'message': f'User with email: {data["email"]} has been created correctly.',
        }