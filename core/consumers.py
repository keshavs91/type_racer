import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from core.redis_rooms import get_room_users


SCORES: dict = {}
TEST_TEXT = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."


class PlayerConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name: str = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name: str = f"room_{self.room_name}"
        SCORES[self.room_group_name] = {}
        _users = get_room_users(self.room_name)
        for u in _users:
            if u not in SCORES[self.room_group_name].keys():
                SCORES[self.room_group_name][u] = {'joined_at': timezone.now().isoformat()}
            else:
                if 'left_at' in SCORES[self.room_group_name][u]:
                    print(f'Not allowed: {u} trying to rejoin {room_name}') 
                    self.close()
                    return

        # player joins game-room websocket group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code): # pyright: ignore
        # player leaves game-room websocket group
        _users = get_room_users(self.room_name)
        for u in _users:
            if u in SCORES[self.room_group_name].keys():
                SCORES[self.room_group_name][u]['left_at'] = timezone.now().isoformat()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data): # pyright: ignore
        text_data_json = json.loads(text_data)
        socket_data = text_data_json

        user_id = socket_data["user_id"]
        message = socket_data["user_input"]
        user_stats = SCORES[self.room_group_name].get(user_id, {})
        if 'started_at' not in user_stats.keys() and len(message) == 1:
            user_stats['started_at'] = timezone.now().isoformat()

        # store user's elapsed time
        # user_stats['elapsed_time_s'] = (user_stats['start_time'] - datetime.now()).total_seconds()
        user_stats['elapsed_time_s'] = 30/60


        # calculate user's scores
        correct_keystroke= 0
        total_keystroke = 1
        for i, _ in enumerate(message):
            if message[i] == TEST_TEXT[i]:
                correct_keystroke += 1

        self.send(text_data=json.dumps({f'message_{user_id}': message, f'message': message}))

        if len(message) > 0:
            total_keystroke = len(message)
        SCORES[self.room_group_name][user_id]['wpm'] = int(total_keystroke/5)/1
        SCORES[self.room_group_name][user_id]['accuracy'] = int((correct_keystroke/total_keystroke))
        print(SCORES)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "game.score", "score": SCORES[self.room_group_name]}
        )

    def game_score(self, event):
        score = event['score']
        self.send(text_data=json.dumps({
            'type': 'score',
            'race_over': False,
            'scores': score
        }))
