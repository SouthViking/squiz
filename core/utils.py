import jwt
import humps
import configparser
from django.conf import settings
from django.http import HttpRequest
from typing import List, Any, Dict, Union

def get_empty_entries(object: dict, target_keys: List[str]) -> List[str]:
    empty_entries = []
    for key in target_keys:
        if key not in object:
            empty_entries.append(key)
            continue
        if type(object[key]) == str and len(object[key].strip()) == 0:
            empty_entries.append(key)
            continue

    return empty_entries

def camelize_list(elements: List[str]):
    for i in range(len(elements)):
        elements[i] = humps.camelize(elements[i])
    
def get_decoded_access_token_from_request(request: HttpRequest) -> Union[str, None]:
    if not hasattr(request, 'META') or request.META.get('HTTP_AUTHORIZATION', None) is None:
        return None

    parts: List[str] = request.META['HTTP_AUTHORIZATION'].split('Bearer ')
    if len(parts) != 2:
        return None

    try:
        # Executing the decoding process, so it can throw an error in case the token is invalid.
        decoded = decode_token(parts[1]) 
        return decoded

    except jwt.InvalidTokenError as error:
        raise error


def import_from_module(module: str, name: str):
    try:
        module = __import__(module, fromlist = [name])
        return getattr(module, name)
    
    except (AttributeError, ModuleNotFoundError):
        return None
    
def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms = ['HS256'])