from django.urls import path
from .views import guest_player, new_game

urlpatterns = [
    path('player/guest', guest_player),
    path('', new_game),
]
