from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class NotificationService:
    def create_notification(self, user, notification_type, title, message, related_id=None):
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_id=related_id
        )
        
        self.send_websocket_notification(user, notification)
        
        return notification
    
    def send_websocket_notification(self, user, notification):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'notification_message',
                'notification': {
                    'id': notification.id,
                    'type': notification.notification_type,
                    'title': notification.title,
                    'message': notification.message,
                    'created_at': str(notification.created_at)
                }
            }
        )
