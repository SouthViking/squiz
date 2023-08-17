from django.test import TestCase
from typing import List, Tuple, Any, Union

from core.utils import decode_token
from users.utils import generate_account_verification_token, generate_authentication_tokens

BASE_USER_DATA = { 'email': 'some_email@example.com' }

def contains_valid_base_token_data(data: dict, check_type: bool = False) -> Tuple[bool, Union[str, None]]:
    expected_properties: List[Tuple[str, Any]] = [('iat', int), ('exp', int), ('email', str)]
    if check_type:
        expected_properties.append(('type', str))

    for property in expected_properties:
        expected_key, expected_value_type = property
        if expected_key not in data:
            return (False, f'Expected key "{expected_key}" not found in token data.')
        if type(data[expected_key]) != expected_value_type:
            return (False, f'Type of value in key "{expected_key}" is {type(data[expected_key])}, but expected is {expected_value_type}.')
        
    return (True, None)


class UserUtilsTests(TestCase):
    def test_account_verification_token_generation(self):
        generated_token = generate_account_verification_token(BASE_USER_DATA)

        self.assertIsNotNone(generated_token, 'Generation token must not be None.')

        decoded_token: dict = decode_token(generated_token)

        is_valid_token, error_message = contains_valid_base_token_data(decoded_token)
        self.assertTrue(is_valid_token, error_message)

    def test_authentication_token_generation(self):
        expected_tokens = ['access_token', 'refresh_token']
        authentication_tokens = generate_authentication_tokens(BASE_USER_DATA)

        for token in expected_tokens:
            self.assertIn(token, authentication_tokens.keys(), f'"{token}" token must be defined in the authentication tokens.')
            decoded_token: dict = decode_token(authentication_tokens[token])

            is_valid_token, error_message = contains_valid_base_token_data(decoded_token, True)
            self.assertTrue(is_valid_token, error_message)