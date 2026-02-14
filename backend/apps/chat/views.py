from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, recipient_id=other_user_id) |
            Q(sender_id=other_user_id, recipient=request.user)
        )
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient == request.user:
            from django.utils import timezone
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            return Response({'message': 'Message marked as read'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
