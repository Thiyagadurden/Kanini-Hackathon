import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_group_name = f'chat_{self.user.id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message')
        recipient_id = data.get('recipient_id')
        
        message = await self.save_message(
            self.user.id,
            recipient_id,
            message_text
        )
        
        await self.channel_layer.group_send(
            f'chat_{recipient_id}',
            {
                'type': 'chat_message',
                'message': message_text,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name(),
                'message_id': message['id'],
                'timestamp': message['created_at']
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, message_text):
        from .models import ChatMessage
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
        message = ChatMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message=message_text
        )
        return {
            'id': message.id,
            'created_at': str(message.created_at)
        }
