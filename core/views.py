import json
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.schema import schema
from core.utils import get_decoded_access_token_from_request

@csrf_exempt
def graphql_executor_view(request: HttpRequest) -> JsonResponse:
    try:
        graphql_request: dict = json.loads(request.body.decode('utf-8'))
        decoded_access_token = get_decoded_access_token_from_request(request)

        result = schema.execute(graphql_request['query'], variables = graphql_request['variables'], context = {
            'token_data': decoded_access_token,
        })

        return JsonResponse({
            'data': result.data,
            'errors': str(result.errors),
        })

    except Exception as error:
        return JsonResponse({
            'success': False,
            'message': 'There has been an internal error. Please try again later.',
            'internal_message': str(error),
        })