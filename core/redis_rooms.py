from django.core.cache import cache


def room_key(room_id: str) -> str:
    return f"room:{room_id}"


def room_exists(room_id: str) -> bool:
    return cache.get(room_key(room_id)) != None


def add_user_to_room(room_id: str, user_id: str):
    print(f'Adding user {user_id} to room {room_id}')
    key = room_key(room_id)
    if not room_exists(room_id):
        cache.set(key, [user_id])
        return True

    users = cache.get(key)
    if users == None:
        users = []
    users.append(user_id)
    cache.set(key, list(set(users)))
    return True


def remove_user_from_room(room_id: str, user_channel_id: str):
    key = room_key(room_id)
    users = cache.get(key)
    if users == None:
        return False
    if len(users) <= 1:
        cache.delete(key)
    else:
        users.remove(user_channel_id)
        cache.set(key, list(set(users)))
    return True


def get_room_users(room_id: str) -> list[str]:
    room_users = cache.get(room_key(room_id))
    if room_users is None:
        return []
    return room_users


def get_all_rooms():
    lobby = cache.get('lobby')
    if not isinstance(lobby, list):
        lobby = []
    return lobby

