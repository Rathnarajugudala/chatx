import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ChatApp.models import Room, Message

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name_param = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"room_{self.room_name_param}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            room_name = data.get('room_name')
            sender = data.get('sender')
            message_text = data.get('message')

            if not all([room_name, sender, message_text]):
                raise ValueError("Missing one or more required fields.")

            message = {
                'room_name': room_name,
                'sender': sender,
                'message': message_text
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': message,
                }
            )

        except (json.JSONDecodeError, ValueError) as e:
            await self.send(text_data=json.dumps({
                'error': f"Invalid message: {str(e)}"
            }))

    async def send_message(self, event):
        data = event['message']

        # Save message to the database
        await self.save_message(data)

        # Send message back to WebSocket
        await self.send(text_data=json.dumps({
            'message': {
                'sender': data['sender'],
                'message': data['message']
            }
        }))

    @database_sync_to_async
    def save_message(self, data):
        try:
            room = Room.objects.get(room_name=data['room_name'])
        except Room.DoesNotExist:
            return  # Or log the issue

        if not Message.objects.filter(
            room=room,
            sender=data['sender'],
            message=data['message']
        ).exists():
            Message.objects.create(
                room=room,
                sender=data['sender'],
                message=data['message']
            )
