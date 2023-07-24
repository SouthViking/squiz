from typing import List, Union
from django.core.exceptions import ValidationError

from .utils import get_empty_entries, camelize_list

def tryable_mutation(required_fields: Union[List[str], None] = None):
    def decorator(func):
        """Adds a try/except wrapper to the target function and returns error messages for some common exceptions."""
        def wrapper(*args, **kwargs):
            try:
                empty_keys = get_empty_entries(kwargs, required_fields)
                if len(empty_keys) != 0:
                    camelize_list(empty_keys)
                    return {
                        'success': False,
                        'message': f'The following fields are empty or haven\'t been specified: {", ".join(empty_keys)}.'
                    }

                return func(*args, **kwargs)

            except ValidationError as error:
                print(error.error_dict)
                return {
                    'success': False,
                    'message': 'There has been a validation error while trying to register the user. Check the required fields and try again.',
                    'internal_message': str(error.error_dict),
                }

            except Exception as error:
                print(error)
                return {
                    'success': False,
                    'message': 'There has been an internal error. Please try again later.',
                    'internal_message': str(error),
                }
            
        return wrapper
    return decorator