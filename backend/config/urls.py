from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def api_root(request):
    return JsonResponse({'message': 'VoiceTriage Hospital OS API', 'version': '1.0.0', 'status': 'running'})

def favicon(request):
    return HttpResponse(status=204)

urlpatterns = [
    path('favicon.ico', favicon, name='favicon'),
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/users/', include('apps.users.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/appointments/', include('apps.appointments.urls')),
    path('api/prescriptions/', include('apps.prescriptions.urls')),
    path('api/nurses/', include('apps.nurses.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/emergency/', include('apps.emergency.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/hospital/', include('apps.hospital.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/audit/', include('apps.audit.urls')),
    path('api/accessibility/', include('apps.accessibility.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
