from datetime import datetime
import os

from flask import Flask, request
import jwt

app = Flask(__name__)
app.debug = True

KEY = None
JWT_ID = 1                              # This needs to be persisted somewhere
SERVICE_ID = 'issuer'
SECONDS_DELTA = 60

USERS = {
    'user1': {'aud': 'calc'},
    'user2': {'aud': 'ingr'},
    'user3': {'aud': 'calc', 'alw': {'calc': ['non-existing']}},
    'user4': {'aud': 'calc', 'alw': {'calc': ['mul']}},
}


def get_key_file():
    global KEY
    if KEY is None:
        with open(os.getenv('KEY', '/key'), 'rb') as f:
            KEY = f.read()
    return KEY


@app.route('/auth/', methods=['POST'])
def authenticate():
    global JWT_ID

    user = request.form.get('user', False)
    if not user:
        app.logger.error('User not provided on the request')
        return '', 400

    if not USERS.get(user, False):
        app.logger.error('User %s not found in %s', user, USERS.keys())
        return '', 401

    now = int(datetime.utcnow().timestamp())
    payload = {
        # Registered claims
        'exp': now + SECONDS_DELTA,
        'iat': now,
        'iss': SERVICE_ID,
        'jti': JWT_ID,
        'sub': user,
        'aud': USERS[user]['aud'],
        # Private claims
        'my:alw': USERS[user].get('alw', {}),
    }

    JWT_ID += 1
    encode = jwt.encode(payload, get_key_file(), algorithm='RS256')
    app.logger.info('User %s generated payload %s', user, payload)
    return encode


if __name__ == '__main__':
    app.run(host='0.0.0.0')
