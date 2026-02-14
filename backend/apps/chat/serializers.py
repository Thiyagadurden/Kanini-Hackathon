from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['created_at', 'read_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name()
    
    def get_recipient_name(self, obj):
        return obj.recipient.get_full_name()
