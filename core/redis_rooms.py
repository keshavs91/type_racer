from datetime import datetime
from django_redis import get_redis_connection

redis = get_redis_connection("default")


def room_exists(room_id: str) -> bool:
    if len(get_room_users(room_id)) > 0:
        return True
    return False


def add_user_to_room(user_id: str, room_id: str):
    key = f'room:{room_id}:users'
    redis.sadd(key, user_id)


def remove_user_from_room(user_id: str, room_id: str,):
    key = f'room:{room_id}:users'
    removed = redis.srem(key, user_id)
    print(f'Remove {user_id} from {room_id}: {bool(removed)}')


def get_room_users(room_id: str) -> list[str]:
    key = f'room:{room_id}:users'
    users = list(redis.smembers(key))
    return [user.decode("utf-8") for user in users]


def set_channel_user(channel_id: str, user_id: str):
    key = f'channel:{channel_id}:user'
    redis.set(key, user_id)


def delete_channel_user(channel_id: str):
    key = f'channel:{channel_id}:user'
    redis.delete(key)


def get_channel_user(channel_id: str) -> str:
    key = f'channel:{channel_id}:user'
    return redis.get(key).decode('utf-8')


def set_game_start(room_id: str, time: str):
    key = f'room:{room_id}:started_at'
    redis.set(key, time)


def get_game_start(room_id: str) -> datetime:
    key = f'room:{room_id}:started_at'
    return datetime.fromisoformat(redis.get(key).decode('utf-8'))

