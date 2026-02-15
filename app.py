from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
import py_db
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SECURE_COOKIES', 'true').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


def make_recipient():
    return secrets.token_hex(6)


@app.route('/')
def index():
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route('/signup')
def signup_page():
    return send_from_directory(PUBLIC_DIR, 'signup.html')


@app.route('/login')
def login_page():
    return send_from_directory(PUBLIC_DIR, 'login.html')


@app.route('/account')
def account_page():
    return send_from_directory(PUBLIC_DIR, 'account.html')


@app.route('/u/<recipient_id>')
def send_page(recipient_id):
    return send_from_directory(PUBLIC_DIR, 'send.html')


@app.route('/inbox')
@app.route('/inbox/')
def inbox_page():
    return send_from_directory(PUBLIC_DIR, 'inbox.html')


@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    ref = data.get('ref') or request.args.get('ref')
    if not username or not password:
        return jsonify({'error':'username and password required'}), 400
    if py_db.get_user_by_username(username):
        return jsonify({'error':'username taken'}), 409
    ph = generate_password_hash(password)
    recipient = make_recipient()
    user = py_db.create_user(username, ph, recipient)
    # if signed up with a ref code, increment referrer's count and give R10 to both
    if ref:
        referrer = py_db.get_user_by_referral_code(ref)
        if referrer:
            py_db.increment_referrals_for_code(ref)
            # Give R10 to new user (by incrementing their referrals count internally)
            # We'll track this in a separate way - add a 'rewardBalance' field
            store = py_db.read_store()
            for u in store.get('users', []):
                if u.get('id') == user['id']:
                    u['rewardBalance'] = u.get('rewardBalance', 0) + 10
                elif u.get('id') == referrer['id']:
                    u['rewardBalance'] = u.get('rewardBalance', 0) + 10
            py_db.write_store(store)
    # set server-side session
    from flask import session
    session['user_id'] = user['id']
    return jsonify({'message':'account created','recipientLink': f'/u/{recipient}','referralCode': user.get('referralCode')}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = py_db.get_user_by_username(username)
    if not user or not check_password_hash(user['passwordHash'], password):
        return jsonify({'error':'invalid credentials'}), 401
    from flask import session
    session['user_id'] = user['id']
    return jsonify({'recipientLink': f'/u/{user["recipientId"]}', 'referralCode': user.get('referralCode')})


@app.route('/api/users/<recipient_id>/messages', methods=['POST'])
def api_send(recipient_id):
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error':'invalid content'}), 400
    mid = py_db.add_message_to_recipient(recipient_id, content)
    if mid is None:
        return jsonify({'error':'recipient not found'}), 404
    return jsonify({'id': mid}), 201


@app.route('/api/logout', methods=['POST'])
def api_logout():
    from flask import session
    session.pop('user_id', None)
    return jsonify({'ok': True})


@app.route('/api/account/messages')
def api_account_messages():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    msgs = py_db.get_messages_for_user(uid, limit=500)
    return jsonify(msgs)


@app.route('/api/account/info')
def api_account_info():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    user = py_db.get_user_by_id(uid)
    if not user:
        return jsonify({'error':'not found'}), 404
    # compute rewards
    refs = user.get('referrals', 0)
    rewards = (refs // 10) * 100  # R100 per 10
    reward_balance = user.get('rewardBalance', 0)
    dev_name = 'SiyamThanda SimeLane'
    return jsonify({
        'username': user.get('username'),
        'recipientLink': f'/u/{user.get("recipientId")}',
        'referralCode': user.get('referralCode'),
        'referrals': refs,
        'rewardsR': rewards,
        'rewardBalance': reward_balance,
        'theme': user.get('theme', 'dark'),
        'linkActive': user.get('linkActive', True),
        'developer': dev_name
    })


@app.route('/api/account/update-theme', methods=['POST'])
def api_update_theme():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    data = request.get_json() or {}
    theme = data.get('theme')
    if theme not in ['dark', 'light']:
        return jsonify({'error':'invalid theme'}), 400
    py_db.update_user_theme(uid, theme)
    return jsonify({'message':'theme updated'}), 200


@app.route('/api/account/toggle-link', methods=['POST'])
def api_toggle_link():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    data = request.get_json() or {}
    active = data.get('active', True)
    py_db.toggle_recipient_link(uid, active)
    return jsonify({'message':'link status updated'}), 200


@app.route('/api/account/regenerate-link', methods=['POST'])
def api_regenerate_link():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    new_link = py_db.generate_new_recipient_link(uid)
    if not new_link:
        return jsonify({'error':'failed to regenerate'}), 500
    return jsonify({'recipientLink': f'/u/{new_link}'}), 200


@app.route('/api/account/change-password', methods=['POST'])
def api_change_password():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    data = request.get_json() or {}
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    if not current_password or not new_password:
        return jsonify({'error':'current password and new password required'}), 400
    if len(new_password) < 6:
        return jsonify({'error':'new password must be at least 6 characters'}), 400
    user = py_db.get_user_by_id(uid)
    if not user or not check_password_hash(user['passwordHash'], current_password):
        return jsonify({'error':'current password is incorrect'}), 401
    # update user password
    new_hash = generate_password_hash(new_password)
    py_db.update_user_password(uid, new_hash)
    return jsonify({'message':'password changed successfully'}), 200


@app.route('/api/account/delete', methods=['POST'])
def api_delete_account():
    from flask import session
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error':'unauthorized'}), 401
    data = request.get_json() or {}
    password = data.get('password', '')
    if not password:
        return jsonify({'error':'password required to delete account'}), 400
    user = py_db.get_user_by_id(uid)
    if not user or not check_password_hash(user['passwordHash'], password):
        return jsonify({'error':'password is incorrect'}), 401
    # delete user
    py_db.delete_user(uid)
    session.pop('user_id', None)
    return jsonify({'message':'account deleted'}), 200


@app.route('/about')
def about_page():
    return send_from_directory(PUBLIC_DIR, 'about.html')


@app.route('/contact')
def contact_page():
    return send_from_directory(PUBLIC_DIR, 'contact.html')


@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()
    if not name or not email or not message:
        return jsonify({'error':'all fields required'}), 400
    # In production, you'd save this to a database or send an email
    # For now, just acknowledge receipt
    print(f"Contact form: {name} ({email}) - {message}")
    return jsonify({'message':'Thank you for contacting us'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
