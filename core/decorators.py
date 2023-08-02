from typing import List, Union
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from users.models import User
from .utils import get_empty_entries, camelize_list

def tryable_mutation(required_fields: Union[List[str], None] = []):
    """
    Adds a try/except wrapper to the target function and returns error messages for some common exceptions.

    Parameters:
        required_fields (List[str]): An optional list containing the required fields. Will return an error response in case any of them are missing.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                empty_keys = get_empty_entries(kwargs, required_fields)
                if len(empty_keys) != 0:
                    camelize_list(empty_keys)
                    return {
                        'success': False,
                        'message': f'The following fields are empty or haven\'t been specified: {", ".join(empty_keys)}.',
                        'status_code': 400,
                    }

                return func(*args, **kwargs)

            except ValidationError as error:
                return {
                    'success': False,
                    'message': 'There has been a validation error while trying to register the user. Check the required fields and try again.',
                    'internal_message': str(error.error_dict),
                    'status_code': 400,
                }

            except Exception as error:
                return {
                    'success': False,
                    'message': 'There has been an internal error. Please try again later.',
                    'internal_message': str(error),
                    'status_code': 500,
                }
            
        return wrapper
    return decorator

def authentication_required_mutation(func):
    """Verifies if the access token was provided and if the user is available before executing the mutator"""
    def wrapper(*args, **kwargs):
        graphql_context: dict = args[1].context

        if graphql_context.get('token_data', None) is None:
            return {
                'success': False,
                'message': 'Access token not provided.',
                'status_code': 401,
            }
        
        if graphql_context['token_data'].get('type', None) != 'access':
            return {
                'success': False,
                'message': 'The provided token is not an access token.',
                'status_code': 400,
            }
        
        try:
            user_record: User = User.objects.get(email = graphql_context['token_data']['email'])
            # Adding the id to the context data so its easier and more efficient when trying to fetch from the mutators.
            args[1].context['user_id'] = user_record.id

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The user account related to the access token is no longer valid.',
                'status_code': 404,
            }

        return func(*args, **kwargs)

    return wrapper