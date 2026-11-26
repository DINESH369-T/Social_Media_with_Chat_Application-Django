import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from proj_3.models import Users
from chat.models import Message

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group = f"chat_{self.room_name}"

        # Get logged-in user from the Django session
        self.username = self.scope["session"].get("username")

        if not self.username:
            await self.close()
            return

        # Identify the other participant in the room
        if self.room_name.startswith(self.username + "_"):
            other_username = self.room_name[len(self.username) + 1:]

        elif self.room_name.endswith("_" + self.username):
            other_username = self.room_name[:-(len(self.username) + 1)]

        else:
            await self.close()
            return

        if not other_username:
            await self.close()
            return

        try:
            self.current_user = await self.get_user(self.username)
            self.other_user = await self.get_user(other_username)

        except Users.DoesNotExist:
            await self.close()
            return

        # Join the conversation group
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )

        await self.accept()

        # Mark messages received by this user as read
        read_message_ids = await self.mark_messages_read(
            self.other_user,
            self.current_user
        )

        # Notify the other participant about read messages
        if read_message_ids:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "read_receipt",
                    "message_ids": read_message_ids,
                    "reader": self.username
                }
            )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group"):
            await self.channel_layer.group_discard(
                self.room_group,
                self.channel_name
            )

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)

            message = data.get("message", "").strip()
            receiver_name = data.get("receiver", "").strip()

            # Sender is always taken from the session
            sender_name = self.username

            if not message or not receiver_name:
                await self.send(text_data=json.dumps({
                    "error": "Message and receiver are required"
                }))
                return

            # Verify that the receiver belongs to this room
            expected_room = "_".join(
                sorted([sender_name, receiver_name])
            )

            if self.room_name != expected_room:
                await self.send(text_data=json.dumps({
                    "error": "Invalid chat room"
                }))
                return

            if receiver_name != self.other_user.username:
                await self.send(text_data=json.dumps({
                    "error": "Invalid receiver"
                }))
                return

            receiver = await self.get_user(receiver_name)

            # Save message
            saved_message = await self.save_message(
                self.current_user,
                receiver,
                message
            )

            # Format timestamp
            message_time = timezone.localtime(
                saved_message.timestamp
            ).strftime("%I:%M %p")

            # Broadcast message to both users
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": sender_name,
                    "message_id": saved_message.id,
                    "timestamp": message_time
                }
            )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid message format"
            }))

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "event": "message",
            "message": event["message"],
            "username": event["username"],
            "message_id": event["message_id"],
            "timestamp": event["timestamp"]
        }))

    async def read_receipt(self, event):

        await self.send(text_data=json.dumps({
            "event": "read_receipt",
            "message_ids": event["message_ids"],
            "reader": event["reader"]
        }))

    @database_sync_to_async
    def get_user(self, username):
        return Users.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            text=message
        )

    @database_sync_to_async
    def mark_messages_read(self, sender, receiver):

        unread_messages = Message.objects.filter(
            sender=sender,
            receiver=receiver,
            is_read=False
        )

        message_ids = list(
            unread_messages.values_list("id", flat=True)
        )

        unread_messages.update(is_read=True)

        return message_ids
