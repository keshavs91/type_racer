from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render


import random
import string

from core.redis_rooms import add_user_to_room, get_room_users, remove_user_from_room, room_exists


# Create your views here.
@api_view(['POST'])
def create_game_room(request):
    if request.method == 'POST':
        data = request.data
        user_id = data.get('user_id', None)
        if user_id is None:
            return Response({'type': 'error', 'message': f'Cannot start game. Invalid user_id'}, status.HTTP_400_BAD_REQUEST)
        chars = string.ascii_uppercase + string.digits
        room_id= ''.join(random.choice(chars) for _ in range(6))
        add_user_to_room(room_id, user_id)
        room_users = get_room_users(room_id)
        return Response({'room_name': room_id, 'can_start': len(room_users) == 2, 'users': room_users}, status.HTTP_200_OK)


@api_view(['POST'])
def join_game_room(request, room_id):
    if request.method == 'POST':
        data = request.data
        user_id = data.get('user_id', None)
        if None in [user_id]:
            return Response({'type': 'error', 'data': {'message': f'Invalid user id {user_id}'}}, status.HTTP_400_BAD_REQUEST)
        if not room_exists(room_id):
            return Response({'type': 'error', 'data': {'message': f'Invalid room id {room_id}'}}, status.HTTP_404_NOT_FOUND)
        add_user_to_room(room_id, user_id)
        room_users = get_room_users(room_id)
        return Response({'room_name': room_id, 'can_start': len(room_users) == 2, 'users': room_users}, status.HTTP_200_OK)


@api_view(['POST'])
def leave_game_room(request, room_id):
    if request.method == 'POST':
        data = request.data
        user_id = data.get('user_id', None)
        if None in [user_id]:
            return Response({'type': 'error', 'data': {'message': f'Invalid user id {user_id}'}}, status.HTTP_400_BAD_REQUEST)
        if not room_exists(room_id):
            return Response({'type': 'error', 'data': {'message': f'Invalid room id {room_id}'}}, status.HTTP_404_NOT_FOUND)
        remove_user_from_room(room_id, user_id)
        room_users = get_room_users(room_id)
        return Response({'room_name': room_id, 'can_start': len(room_users) == 2, 'users': room_users}, status.HTTP_200_OK)


def home(request):
    return render(request, 'core/index.html')


def game_room(request, room_id: str):
    if room_exists(room_id):
        room_users = get_room_users(room_id)
        return render(request, 'core/game_room.html', {'room_name': room_id, 'can_start': len(room_users) == 2, 'users': room_users})

