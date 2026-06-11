import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class OrderConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for kitchen order board.

    Clients connect to ws://host/ws/orders/<restaurant_id>/
    and receive JSON messages when orders change status.

    Message format sent to clients:
        {"type": "order_update", "order_id": 42, "status": "in_progress"}
    """

    async def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.group_name = f'orders_{self.restaurant_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.debug('WS connected: group=%s', self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Clients don't send messages; ignore any incoming data.
        pass

    # Handler called by channel_layer.group_send(type="order_update")
    async def order_update(self, event):
        await self.send(text_data=json.dumps(event))
