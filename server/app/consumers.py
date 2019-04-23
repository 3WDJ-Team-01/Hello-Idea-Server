from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from .models import *
from .serializers import *
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer

@receiver(post_save, sender=Request)
def request(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        send_id = instance.send_id_id
        send_name = User.objects.filter(user_id=send_id).values('user_name')
        receive_id = instance.receive_id
        receive_name = User.objects.filter(user_id=receive_id).values('user_name')
        shares = "shares" + str(receive_id)
        async_to_sync(channel_layer.group_send)(
            shares, {
                "type": "share_message",
                "send_name": send_name[0]['user_name'],
                "receive_name": receive_name[0]['user_name'],
                "message": instance.request_cont,
            }
    )

@receiver(post_save, sender=Notification)
def notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        send_id = instance.send_id_id
        send_name = User.objects.filter(user_id=send_id).values('user_name')
        receive_id = instance.receive_id
        receive_name = User.objects.filter(user_id=receive_id).values('user_name')
        shares = "shares" + str(receive_id)
        async_to_sync(channel_layer.group_send)(
            shares, {
                "type": "share_message",
                "send_name": send_name[0]['user_name'],
                "receive_name": receive_name[0]['user_name'],
                "message": instance.notify_cont,
            }
    )

# alarm
class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'shares%s' % self.user_id
        print(self.room_group_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    def share_message(self, event):
        message = event['message']
        send_name = event['send_name']
        receive_name = event['receive_name']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "send_name": send_name,
            "receive_name": receive_name,
            'message': message
        }))