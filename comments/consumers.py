
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class CommentConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "comments",
            self.channel_name
        )

        await self.accept()

        await self.send_json({
            "message": "WebSocket connected"
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "comments",
            self.channel_name
        )

    async def comment_created(self, event):
        await self.send_json({
            "event": "comment.created",
            "comment": event["comment"]
        })
