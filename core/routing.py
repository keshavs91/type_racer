from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/player/(?P<player_id>[0-9a-fA-F-]+)/$", consumers.PlayerConsumer.as_asgi()),
    re_path(r"ws/room/(?P<room_name>\w+)/$", consumers.PlayerConsumer.as_asgi()),
]
