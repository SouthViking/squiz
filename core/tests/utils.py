from django.test import TestCase
from django.http import HttpRequest

from users.utils import generate_authentication_tokens
from core.utils import get_empty_entries, get_decoded_access_token_from_request, decode_token

class CoreUtilsTests(TestCase):
    def test_get_empty_entries(self):
        # Should detect when a key is required, exists in the object, but is empty.
        object = {
            'key1': '',
            'key2': 'a',     
            'key3': '    ',       
        }
        expected_empty_entries = ['key1', 'key3']
        real_empty_entries = get_empty_entries(object, ['key1', 'key2', 'key3'])
        
        self.assertEqual(expected_empty_entries, real_empty_entries, f'Empty entries must be {expected_empty_entries}, got {real_empty_entries}.')

        # Should detect when a key is required, but it does not exist in the object.
        object = {
            'key1': 'a',
            'key3': 'b',
            'key5': 'c'
        }
        expected_empty_entries = ['key2', 'key4']
        real_empty_entries = get_empty_entries(object, ['key1', 'key2', 'key3', 'key4'])

        self.assertEqual(expected_empty_entries, real_empty_entries, f'Empty entries must be {expected_empty_entries}, got {real_empty_entries}.')

        # Should detect when a key is required and defined correctly.
        object = {
            'key1': 'a',
            'key2': 'b',
            'key3': 'c',
            'key4': 'd',
        }
        expected_empty_entries = []
        real_empty_entries = get_empty_entries(object, ['key1', 'key2', 'key3', 'key4'])

        self.assertEqual(expected_empty_entries, real_empty_entries, f'Empty entries must be {expected_empty_entries}, got {real_empty_entries}.')
    
    def test_access_token_decode_from_request(self):
        fake_request = HttpRequest()

        expected_token = None
        real_decoded_token = get_decoded_access_token_from_request(fake_request)

        self.assertEqual(expected_token, real_decoded_token, f'Token data must be None since the request does not contain an authorization header.')

        fake_request.META['HTTP_AUTHORIZATION'] = ''
        real_decoded_token = get_decoded_access_token_from_request(fake_request)

        self.assertEqual(expected_token, real_decoded_token, f'Token data must be None since the request contains the "HTTP_AUTHORIZATION" key, however it is empty.')

        tokens = generate_authentication_tokens({})

        fake_request.META['HTTP_AUTHORIZATION'] = f'Bearer {tokens["access_token"]}'
        real_decoded_token = get_decoded_access_token_from_request(fake_request)

        self.assertEqual(decode_token(tokens['access_token']), real_decoded_token, f'Token must be fetched from the authorization header. Expected: {tokens["access_token"]} | Real: {real_decoded_token}')