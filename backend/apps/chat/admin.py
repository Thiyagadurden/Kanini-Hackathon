from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
