import jwt
import graphene
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, timezone
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from core.decorators import tryable_mutation
from users.utils import generate_account_verification_token, generate_authentication_tokens

def generate_and_send_email_verification_token(user_email: str):
    verification_token = generate_account_verification_token({ 'email': user_email })

    user_record = User.objects.get(email = user_email)
    user_record.verification_token = verification_token
    user_record.save()

    send_mail(
        subject = 'Welcome to Squiz!',
        message = f'Welcome to Squiz! In order to continue using your new account, please verify your email using the following link: https://squiz.com/account/verification/{verification_token}',
        recipient_list = [user_email],
        from_email = settings.EMAIL_HOST_USER
    )

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

        generate_and_send_email_verification_token(data['email'])

        return {
            'success': True,
            'message': f'User with email: {data["email"]} has been created correctly.',
        }
    
class ResendEmailVerificationTokenMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required = True)

    class Meta:
        description = 'Sends the email verification token again to the user email. Use it when the initial email is not received during the registration mutation.'
    
    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()

    @tryable_mutation(required_fields = ['email'])
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(email = data['email'])
            if user_record.is_verified:
                return {
                    'success': False,
                    'message': f'The user with email: {data["email"]} has already been verified.',
                }
            
            if user_record.verification_token is not None:
                current_verification_token: dict = jwt.decode(user_record.verification_token, settings.SECRET_KEY, algorithms = ['HS256'])
                if current_verification_token.get('iat', None) is not None:
                    elapsed_since_iat_mins = int(round((datetime.now() - datetime.fromtimestamp(current_verification_token['iat'])).total_seconds()/60, 0))

                    if elapsed_since_iat_mins < settings.EMAIL_VERIFICATION_MIN_GAP_MINS:
                        remaining_time_mins = settings.EMAIL_VERIFICATION_MIN_GAP_MINS - elapsed_since_iat_mins

                        return {
                            'success': False,
                            'message': f'A verification email was already sent {elapsed_since_iat_mins} minutes ago. You can request again in more {remaining_time_mins} mins.'
                        }

            
            generate_and_send_email_verification_token(data['email'])

            return {
                'success': True,
                'message': f'A new verification link has been sent to the email: {data["email"]}',
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': f'The user with email: {data["email"]} does not exist.',
            }
        

class EmailVerificationMutation(graphene.Mutation):
    class Arguments:
        token = graphene.String()
    
    class Meta:
        description = 'Marks the account linked to the token as verified.'

    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()

    @tryable_mutation(required_fields = ['token'])
    def mutate(root, info, **data):
        try:
            decoded_token: dict = jwt.decode(data['token'], settings.SECRET_KEY, algorithms = ['HS256'])
            if decoded_token.get('email', None) is None:
                return {
                    'success': False,
                    'message': 'The current token has an invalid format. Please request a new one.',
                }
            
            user_record: User = User.objects.get(email = decoded_token['email'])

            if user_record.is_verified:
                return {
                    'success': False,
                    'message': f'The account with email: {decoded_token["email"]} has already been verified.',
                }

            user_record.is_verified = True
            user_record.verification_token = None

            user_record.save()

            return {
                'success': True,
                'message': f'The account with email: {decoded_token["email"]} has been verified.',
            }
        
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'message': 'Cannot verify the account. The token is expired.',
            }
        
        except jwt.InvalidSignatureError:
            return {
                'success': False,
                'message': 'The token couldn\'t be processed. The format is incorrect.',
            }
        
        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': f'The user with email: {decoded_token["email"]} does not exist.',
            }
        
class AuthenticationTokenResponse(graphene.ObjectType):
    access_token = graphene.String()
    refresh_token = graphene.String()
        
class UserAuthenticationMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required = True)
        password = graphene.String(required = True)

    class Meta:
        description = 'Executes the authentication process and returns the access and refresh token.'

    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()
    tokens = graphene.Field(AuthenticationTokenResponse)

    @tryable_mutation(required_fields = ['email', 'password'])
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(email = data['email'])
            if not user_record.check_password(data['password']):
                return {
                    'success': False,
                    'message': 'The provided credentials are not valid. Please try again.'
                }
            
            user_record.last_login = datetime.now(tz = timezone.utc)
            user_record.save(update_fields = ['last_login'])
            
            return {
                'success': True,
                'message': f'Welcome again {user_record.nickname}!',
                'tokens': generate_authentication_tokens({ 'email': data['email'] }),
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The provided credentials are not valid. Please try again.'
            }

class TokenRefreshMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required = True)

    class Meta:
        description = 'Generates a new access/refresh token pair by using the current refresh token.'

    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()
    tokens = graphene.Field(AuthenticationTokenResponse)

    @tryable_mutation(required_fields = ['refresh_token'])
    def mutate(root, info, **data):
        try:
            decoded_token: dict = jwt.decode(data['refresh_token'], settings.SECRET_KEY, algorithms = ['HS256'])
            if decoded_token.get('type', None) != 'refresh':
                return {
                    'success': False,
                    'message': 'The token provided is not a valid refresh token.'
                }

            User.objects.get(email = decoded_token['email'])

            return {
                'success': True,
                'tokens': generate_authentication_tokens({ 'email': decoded_token['email'] }),
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'message': 'The refresh token is expired. Please execute the authentication again.'
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The source account is not valid.',
            }