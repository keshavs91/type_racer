from django.http import JsonResponse
from django.shortcuts import render
import uuid

# Create your views here.

def guest_player(request):
    return JsonResponse(data={'player_id': uuid.uuid4()})

def new_game(request):
    return render(request, 'core/new_game.html')
