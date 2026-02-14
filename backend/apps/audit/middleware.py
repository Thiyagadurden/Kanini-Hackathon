from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete'
            }
            
            request.audit_data = {
                'user': request.user,
                'action': action_map.get(request.method),
                'ip_address': ip_address,
                'user_agent': user_agent
            }
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
