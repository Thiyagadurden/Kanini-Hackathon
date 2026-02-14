from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello from Django backend!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/', hello_world),
]
