import graphene
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email

from users.models import User
from core.decorators import tryable_mutation
from users.utils import generate_account_verification_token

class RegistrationMutation(graphene.Mutation):
    class Arguments:
        full_name = graphene.String(required = True)
        nickname = graphene.String(required = True)
        email = graphene.String(required = True)
        password = graphene.String(required = True)

    class Meta:
        description = 'Executes the process to register a new user in the platform.'

    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()

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

        email_verification_token = generate_account_verification_token({ 'email': data['email'] })

        user_record: User = User.objects.get(email = data['email'])
        user_record.verification_token = email_verification_token
        user_record.save()

        send_mail(
            subject = 'Welcome to Squiz!',
            message = f'Welcome to Squiz! In order to continue using your new account, please verify your email using the following link: https://squiz.com/account/verification/{email_verification_token}',
            recipient_list = [data['email']],
            from_email = settings.EMAIL_HOST_USER
        )


        return {
            'success': True,
            'message': f'User with email: {data["email"]} has been created correctly.'
        }