import json
from datetime import timedelta
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from core.redis_rooms import add_user_to_room, get_game_start, get_room_users, remove_user_from_room, set_channel_user, delete_channel_user, get_channel_user, set_game_start


# SCORES: dict = {}
TEST_TEXT = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."


class PlayerConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name: str = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name: str = f"room_{self.room_name}"
        # SCORES[self.room_group_name] = {}
        # _users = get_room_users(self.room_name)
        # for u in _users:
        #     if u not in SCORES[self.room_group_name].keys():
        #         SCORES[self.room_group_name][u] = {'joined_at': timezone.now().isoformat()}
        #     else:
        #         if 'left_at' in SCORES[self.room_group_name][u]:
        #             print(f'Not allowed: {u} trying to rejoin {self.room_name}') 
        #             self.close()
        #             return

        # add user to room's websocket group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, code): # pyright: ignore
        # player leaves game-room websocket group
        # _users = get_room_users(self.room_name)
        # for u in _users:
        #     if u in SCORES[self.room_group_name].keys():
        #         SCORES[self.room_group_name][u]['left_at'] = timezone.now().isoformat()

        # remove user from room's websocket group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
        remove_user_from_room(get_channel_user(self.channel_name), self.room_name)
        delete_channel_user(self.channel_name)

        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {'type': 'players_update', 'log': f'user removed from room {self.room_name}'})

    def receive(self, text_data): # pyright: ignore
        socket_data  = json.loads(text_data)
        print(socket_data)
        event = socket_data.get('event')

        if event == 'join':
            data = socket_data.get('data', {})
            user_id = data.get('user_id')
            if user_id is None:
                self.close()
                raise Exception('Invalid User Id')
            add_user_to_room(user_id, self.room_name)
            set_channel_user(self.channel_name, user_id)

            async_to_sync(self.channel_layer.group_send)(self.room_group_name, {'type': 'players_update', 'log': f'user added to room {self.room_name}'})

            # if enough players joined then start game
            if len(get_room_users(self.room_name)) >= 3:
                async_to_sync(self.channel_layer.group_send)(self.room_group_name, {'type': 'game_start', 'log': f'Starting game in room {self.room_name}'})

        elif event == 'player_progress':
            data = socket_data.get('data', {})
            user_id = data.get('user_id')
            if user_id is None:
                self.close()
                raise Exception('Invalid User Id')

            # calculate user's scores
            message = data.get('user_input', '')
            correct_keystroke= 0
            total_keystroke = 1
            for i, _ in enumerate(message):
                if message[i] == TEST_TEXT[i]:
                    correct_keystroke += 1
            elapsed_time_m = (timezone.now()- get_game_start(self.room_name)).total_seconds() / 60

            self.send(text_data=json.dumps({
                'event': 'player_progress',
                'data': {
                    'typed_text': message,
                    'wpm': int((total_keystroke/5)/(elapsed_time_m)),
                    'accuracy': int((correct_keystroke/total_keystroke)),
                }
            }))

    def players_update(self, event: dict):
        room_users = get_room_users(self.room_name)
        print(event['log'])
        self.send(text_data=json.dumps({
            'event': event['type'],
            'data': {
                'users': room_users,
                'can_start': len(room_users) > 2,
            }
        }))

    def game_start(self, event: dict):
        now = timezone.now()
        self.send(text_data=json.dumps({
            'event': event['type'],
            'data': {
                'paragraph': TEST_TEXT,
                'start_at': (now + timedelta(seconds=5)).isoformat(),
                'run_until': (now + timedelta(seconds=30)).isoformat(),
            }
        }))
        set_game_start(self.room_name, (now+timedelta(seconds=5)).isoformat())

