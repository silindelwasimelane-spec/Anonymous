import json
import os
import secrets
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
STORE_PATH = os.path.join(DATA_DIR, 'store.json')

def _ensure_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def read_store():
    _ensure_dir()
    try:
        with open(STORE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"nextMsgId":1, "messages":[], "nextUserId":1, "users":[], "tokens":{}}

def write_store(store):
    _ensure_dir()
    tmp = STORE_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(store, f)
    os.replace(tmp, STORE_PATH)

def create_user(username: str, password_hash: str, recipient_id: str):
    store = read_store()
    id = store["nextUserId"]
    # generate a referral code for this user
    referral_code = secrets.token_hex(4)
    user = {
        "id": id,
        "username": username,
        "passwordHash": password_hash,
        "recipientId": recipient_id,
        "referralCode": referral_code,
        "referrals": 0,
        "theme": "dark",
        "linkActive": True,
        "customLinks": []
    }
    store["nextUserId"] += 1
    store["users"].append(user)
    write_store(store)
    return user

def get_user_by_username(username: str) -> Optional[dict]:
    store = read_store()
    for u in store.get('users', []):
        if u.get('username') == username:
            return u
    return None

def get_user_by_id(uid: int) -> Optional[dict]:
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == uid:
            return u
    return None

def get_user_by_recipient(recipient_id: str) -> Optional[dict]:
    store = read_store()
    for u in store.get('users', []):
        if u.get('recipientId') == recipient_id:
            return u
    return None

def get_user_by_referral_code(code: str) -> Optional[dict]:
    store = read_store()
    for u in store.get('users', []):
        if u.get('referralCode') == code:
            return u
    return None

def increment_referrals_for_code(code: str):
    store = read_store()
    for u in store.get('users', []):
        if u.get('referralCode') == code:
            u['referrals'] = u.get('referrals', 0) + 1
            write_store(store)
            return True
    return False

def add_message_to_recipient(recipient_id: str, content: str) -> Optional[int]:
    store = read_store()
    user = get_user_by_recipient(recipient_id)
    if not user:
        return None
    mid = store['nextMsgId']
    store['nextMsgId'] += 1
    msg = {"id": mid, "userId": user['id'], "content": content, "created_at": int(__import__('time').time() * 1000)}
    store['messages'].insert(0, msg)
    if len(store['messages']) > 10000:
        store['messages'] = store['messages'][:10000]
    write_store(store)
    return mid

def get_messages_for_user(user_id: int, limit: int = 100):
    store = read_store()
    return [m for m in store.get('messages', []) if m.get('userId') == user_id][:limit]

def set_token(token: str, user_id: int):
    store = read_store()
    store['tokens'][token] = user_id
    # attach token to user object for easy lookup
    for u in store.get('users', []):
        if u.get('id') == user_id:
            u['token'] = token
            break
    write_store(store)

def get_userid_by_token(token: str) -> Optional[int]:
    store = read_store()
    return store.get('tokens', {}).get(token)

def get_token_for_user(user_id: int) -> Optional[str]:
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == user_id:
            return u.get('token')
    return None

def ensure_token_for_user(user_id: int) -> str:
    t = get_token_for_user(user_id)
    if t:
        return t
    t = secrets.token_hex(24)
    set_token(t, user_id)
    return t

def update_user_password(user_id: int, new_password_hash: str):
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == user_id:
            u['passwordHash'] = new_password_hash
            write_store(store)
            return True
    return False

def delete_user(user_id: int):
    store = read_store()
    # remove user
    store['users'] = [u for u in store.get('users', []) if u.get('id') != user_id]
    # remove all messages for this user
    store['messages'] = [m for m in store.get('messages', []) if m.get('userId') != user_id]
    write_store(store)
    return True

def update_user_theme(user_id: int, theme: str):
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == user_id:
            u['theme'] = theme
            write_store(store)
            return True
    return False

def toggle_recipient_link(user_id: int, active: bool):
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == user_id:
            u['linkActive'] = active
            write_store(store)
            return True
    return False

def generate_new_recipient_link(user_id: int):
    store = read_store()
    for u in store.get('users', []):
        if u.get('id') == user_id:
            new_link = secrets.token_hex(6)
            u['recipientId'] = new_link
            write_store(store)
            return new_link
    return None

