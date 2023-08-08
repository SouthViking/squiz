import jwt
import graphene
from django.conf import settings
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist

from .. import logger
from users.models import User
from core.utils import decode_token
from core.decorators import tryable_mutation
from core.graphene.common import BaseMutationResult
from users.utils import generate_authentication_tokens

class AuthenticationTokenResponse(graphene.ObjectType):
    access_token = graphene.String()
    refresh_token = graphene.String()

class UserAuthenticationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        email = graphene.String(required = True)
        password = graphene.String(required = True)

    class Meta:
        description = 'Executes the authentication process and returns the access and refresh token.'

    tokens = graphene.Field(AuthenticationTokenResponse)

    @tryable_mutation(required_fields = ['email', 'password'])
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(email = data['email'])
            if not user_record.check_password(data['password']):
                logger.warn(f'Authentication for account with ID {user_record.id} failed. Password was incorrect.')
                return {
                    'success': False,
                    'message': 'The provided credentials are not valid. Please try again.',
                    'status_code': 401,
                }
            
            logger.info(f'Executing authentication process for verified account with ID {user_record.id}.')
            
            logger.info(f'Last login for account with ID {user_record.id} was on {str(user_record.last_login.replace(microsecond = 0))}')
            user_record.last_login = datetime.now(tz = timezone.utc)
            user_record.save(update_fields = ['last_login'])
            
            return {
                'success': True,
                'message': f'Welcome again {user_record.nickname}!',
                'tokens': generate_authentication_tokens({ 'email': data['email'] }),
                'status_code': 200,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The provided credentials are not valid. Please try again.',
                'status_code': 401,
            }
        

class TokenRefreshMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        refresh_token = graphene.String(required = True)

    class Meta:
        description = 'Generates a new access/refresh token pair by using the current refresh token.'

    tokens = graphene.Field(AuthenticationTokenResponse)

    @tryable_mutation(required_fields = ['refresh_token'])
    def mutate(root, info, **data):
        try:
            decoded_token: dict = decode_token(data['refresh_token'])
            if decoded_token.get('type', None) != 'refresh':
                return {
                    'success': False,
                    'message': 'The token provided is not a valid refresh token.',
                    'status_code': 400,
                }
            
            
            logger.info(f'Executing token refresh process for account with email {decoded_token["email"]}')
            logger.debug(f'Status of the current refresh token:')
            logger.debug(f'iat = {decoded_token["iat"]} ({datetime.fromtimestamp(decoded_token["iat"])}) | exp = {decoded_token["exp"]} ({datetime.fromtimestamp(decoded_token["exp"])}).')

            tokens = generate_authentication_tokens({ 'email': decoded_token['email'] })
            decoded_access_token = decode_token(tokens['access_token'])

            logger.debug(f'New access token generated with the following timestamps:')
            logger.debug(f'iat: iat = {decoded_access_token["iat"]} ({datetime.fromtimestamp(decoded_access_token["iat"])}) | exp = {decoded_access_token["exp"]} ({datetime.fromtimestamp(decoded_access_token["exp"])})')

            return {
                'success': True,
                'tokens': tokens,
                'status_code': 200,
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'message': 'The refresh token is expired. Please execute the authentication again.',
                'status_code': 401,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The source account is not valid.',
                'status_code': 404,
            }