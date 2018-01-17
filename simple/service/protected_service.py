from functools import wraps
import os

from flask import Flask
from flask import request
import jwt

SERVICE_ID = 'calc'
ISSUER = 'issuer'
app = Flask(SERVICE_ID)
app.debug = True
KEY = None


def get_key_file():
    global KEY
    if KEY is None:
        with open(os.getenv('KEY', '/key.pub'), 'rb') as f:
            KEY = f.read()
    return KEY


def valid_token(action, token):
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

    app.logger.info('Token decoded %s', decoded_token)
    if action is not None and (
        'my:alw' not in decoded_token or
        action not in decoded_token['my:alw'].get(SERVICE_ID, [])
    ):
        app.logger.error(
            'User %s is not allowed to %s',
            decoded_token['sub'], action
        )
        return False

    return True


def jwt_required(action=None):
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            token = request.headers.get('Authorization', False)

            if not token:
                return '', 401
            if not valid_token(action, token):
                return '', 403

            return f(*args, **kwargs)
        return decorated_func
    return decorator


@app.route('/mul/', methods=['POST'])
@jwt_required('mul')
def mul():
    num1 = request.form.get('num1', False)
    num2 = request.form.get('num2', False)

    if not num1 or not num2:
        return '0'

    app.logger.info('User request to multiply %s with %s', num1, num2)
    return str(int(num1) * int(num2))


@app.route('/sum/', methods=['POST'])
@jwt_required()
def sum():
    num1 = request.form.get('num1', False)
    num2 = request.form.get('num2', False)

    if not num1 or not num2:
        return '0'

    app.logger.info(request.args)
    app.logger.info('User request to sum %s and %s', num1, num2)
    return str(int(num1) + int(num2))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
