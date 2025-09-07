import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from channels.generic.websocket import AsyncWebsocketConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Adm.settings")
django_asgi_app = get_asgi_application()

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(text_data=text_data)
        elif bytes_data:
            await self.send(bytes_data=bytes_data)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter([
        path("ws/echo/", EchoConsumer.as_asgi()),
    ]),
})
