from .models import ChatMessage

class ChatService:
    def send_message(self, sender, recipient, message):
        chat_message = ChatMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message=message
        )
        return chat_message
    
    def get_conversation(self, user1, user2):
        from django.db.models import Q
        return ChatMessage.objects.filter(
            Q(sender=user1, recipient=user2) |
            Q(sender=user2, recipient=user1)
        )
