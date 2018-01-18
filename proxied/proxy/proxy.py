from datetime import datetime
from functools import wraps
import os

from flask import Flask, request
import requests
import jwt

app = Flask(__name__)
app.debug = True

PUB_KEY = None
SECRET = os.getenv('SECRET', 'super-secret')
SERVICE_ID = 'proxy'
ISSUER = 'issuer'
SECONDS_DELTA = 60


ACTIONS_TO_PROFILE = {
    'calc': ['accountant-full', 'accountant-simple'],
    'ingr': ['nutritionist'],
}

PROFILE_TO_ALW = {
    'accountant-full': {'aud': 'calc', 'alw': {'calc': ['mul']}},
    'accountant-simple': {'aud': 'calc'},
    'nutritionist': {'aud': 'ingr'},
}

PROCESSING_TOKENS = []


def generate_internal_token(token):
    claim = 'proxy:prf'
    new_token = {
        'iss': SERVICE_ID,
        'iat': int(datetime.utcnow().timestamp()),
        'jti': token['jti'],
        'sub': token['sub'],
        'aud': PROFILE_TO_ALW[token[claim]]['aud'],
        'my:alw': PROFILE_TO_ALW[token[claim]].get('alw', {}),
    }
    app.logger.info(
        'Generated internal token %s from valid request', new_token
    )
    return jwt.encode(new_token, SECRET, algorithm='HS256')


def get_key_file():
    global PUB_KEY
    if PUB_KEY is None:
        with open(os.getenv('PUB_KEY', '/key.pub'), 'rb') as f:
            PUB_KEY = f.read()
    return PUB_KEY


def valid_token(action, profiles, token):
    if not token.startswith('Bearer '):
        return False

    try:
        decoded_token = jwt.decode(
            token[7:], get_key_file(),
            audience=SERVICE_ID,
            issuer=ISSUER,
            algorithm='RS256'
        )
    except jwt.exceptions.InvalidTokenError as e:
        app.logger.error('Invalid Token error `%s`', str(e))
        return False

    if decoded_token['jti'] in PROCESSING_TOKENS:
        app.logger.error('Previous request still running.')
        return False

    app.logger.info('Token decoded %s', decoded_token)
    claim = 'proxy:prf'
    if profiles is not None and (
        claim not in decoded_token or
        decoded_token[claim] not in profiles
    ):
        app.logger.error(
            'User %s is not allowed %s with profile %s',
            decoded_token['sub'], action, decoded_token[claim]
        )
        return False

    PROCESSING_TOKENS.append(decoded_token['jti'])
    return decoded_token


def jwt_required(action=None):
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            token = request.headers.get('Authorization', False)

            if not token:
                return '', 401

            decoded_token = valid_token(
                action, ACTIONS_TO_PROFILE[action], token
            )

            if not decoded_token:
                return '', 403

            kwargs['internal_token'] = {
                'jti': decoded_token['jti'],
                'token': generate_internal_token(decoded_token)
            }
            return f(*args, **kwargs)
        return decorated_func
    return decorator


@app.route('/calc/<path:path>', methods=['POST'])
@jwt_required('calc')
def proxy_request(path, internal_token):
    host = 'http://calc:5000/{}'.format(path)
    headers = {
        'Authorization': 'Bearer {0}'.format(
            internal_token['token'].decode('utf-8')
        )
    }
    response = requests.post(host, data=request.form, headers=headers)

    PROCESSING_TOKENS.remove(internal_token['jti'])
    return response.text


if __name__ == '__main__':
    app.run(host='0.0.0.0')
