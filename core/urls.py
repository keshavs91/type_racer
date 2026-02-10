from django.urls import path
from .views import home, create_game_room, join_game_room, leave_game_room, game_room

urlpatterns = [
    path('', home),
    path('room/create', create_game_room, name='create_room'),
    path('room/<str:room_id>', game_room),
    path('room/<str:room_id>/join', join_game_room),
    path('room/<str:room_id>/leave', leave_game_room),
]
