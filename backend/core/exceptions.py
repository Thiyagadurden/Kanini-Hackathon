from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
            'details': response.data
        }
        return Response(custom_response, status=response.status_code)
    
    return response

class PermissionDenied(Exception):
    pass

class NotFound(Exception):
    pass

class BadRequest(Exception):
    pass
