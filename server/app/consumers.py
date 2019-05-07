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
                "id": instance.request_id,
                "send_name": send_name[0]['user_name'],
                "receive_name": receive_name[0]['user_name'],
                "message": "requests",
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
                "id": instance.notify_id,
                "send_name": send_name[0]['user_name'],
                "receive_name": receive_name[0]['user_name'],
                "message": "notifications",
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
        id = event['id']
        message = event['message']
        send_name = event['send_name']
        receive_name = event['receive_name']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "id": id,
            "send_name": send_name,
            "receive_name": receive_name,
            'message': message
        }))
# chatting
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        # chat_id 번호로 채널의 그룹 이름을 짓습니다.
        self.room_group_name = 'chat_%s' % self.chat_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        chat_id = text_data_json['chat_id']
        message = text_data_json['message']
        user_name = text_data_json['user_name']

        user_id = User.objects.filter(user_name=user_name).values('user_id')
        Chat_cont.objects.create(chat_id_id=chat_id, user_id_id=user_id[0]['user_id'], chat_cont=message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_name': user_name,
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))