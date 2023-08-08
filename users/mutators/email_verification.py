import jwt
import graphene
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .. import logger
from users.models import User
from core.utils import decode_token
from core.decorators import tryable_mutation
from core.graphene.common import BaseMutationResult
from users.utils import generate_and_send_email_verification_token

class EmailVerificationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        token = graphene.String()
    
    class Meta:
        description = 'Marks the account linked to the token as verified.'

    @tryable_mutation(required_fields = ['token'])
    def mutate(root, info, **data):
        try:
            decoded_token: dict = decode_token(data['token'])
            if decoded_token.get('email', None) is None:
                return {
                    'success': False,
                    'message': 'The current token has an invalid format. Please request a new one.',
                    'status_code': 400,
                }
            
            user_record: User = User.objects.get(email = decoded_token['email'])

            if user_record.is_verified:
                return {
                    'success': False,
                    'message': f'The account with email: {decoded_token["email"]} has already been verified.',
                    'status_code': 409,
                }
            
            logger.info(f'Executing email verification for account with ID {user_record.id}.')

            user_record.is_verified = True
            user_record.verification_token = None

            user_record.save()

            return {
                'success': True,
                'message': f'The account with email: {decoded_token["email"]} has been verified.',
                'status_code': 200,
            }
        
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'message': 'Cannot verify the account. The token is expired.',
                'status_code': 401,
            }
        
        except jwt.InvalidSignatureError:
            return {
                'success': False,
                'message': 'The token couldn\'t be processed. The format is incorrect.',
                'status_code': 400,
            }
        
        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': f'The user with email: {decoded_token["email"]} does not exist.',
                'status_code': 404,
            }
        
class ResendEmailVerificationTokenMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        email = graphene.String(required = True)

    class Meta:
        description = 'Sends the email verification token again to the user email. Use it when the initial email is not received during the registration mutation.'

    @tryable_mutation(required_fields = ['email'])
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(email = data['email'])
            if user_record.is_verified:
                return {
                    'success': False,
                    'message': f'The user with email: {data["email"]} has already been verified.',
                    'status_code': 409,
                }
            
            logger.info(f'Executing mutation to resend email verification for account with ID {user_record.id}')
            
            if user_record.verification_token is not None:
                current_verification_token = decode_token(user_record.verification_token)
                elapsed_since_iat_mins = int(round((datetime.now() - datetime.fromtimestamp(current_verification_token['iat'])).total_seconds()/60, 0))

                if elapsed_since_iat_mins < settings.EMAIL_VERIFICATION_MIN_GAP_MINS:
                    remaining_time_mins = settings.EMAIL_VERIFICATION_MIN_GAP_MINS - elapsed_since_iat_mins

                    return {
                        'success': False,
                        'message': f'A verification email was already sent {elapsed_since_iat_mins} minutes ago. You can request again in more {remaining_time_mins} mins.',
                        'status_code': 409,
                    }
            
            generate_and_send_email_verification_token(data['email'])

            return {
                'success': True,
                'message': f'A new verification link has been sent to the email: {data["email"]}',
                'status_code': 200,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': f'The user with email: {data["email"]} does not exist.',
                'status_code': 404,
            }