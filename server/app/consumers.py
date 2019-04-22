from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
import json
from .models import *
from .serializers import *

# alarm
class NotificationConsumer(WebsocketConsumer):

    async def connect(self):
        self.notify_id = self.scope['url_route']['kwargs']['notify_id']
        # chat_id 번호로 채널의 그룹 이름을 짓습니다.
        self.room_group_name = 'chat_%s' % self.notify_id

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # Receive message from WebSocket
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
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