import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'el-diablo.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://auth0.coffee.shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header


def get_token_auth_header():
    '''Obtains access token from the Authorization header in the request object
    '''
    auth_header = request.headers.get('Authorization', None)
    # Error handler for the absence of authentication header
    if auth_header == None:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected in request.'
        }, 401)
    
    header_parts = auth_header.split(' ')
    # Confirm type of token is bearer
    if header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    
    elif len(header_parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    
    elif len(header_parts) > 2:
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = header_parts[1]
    return token


def check_permissions(permission, payload):
    '''
    Function for checking the presence of "permissions" in JWT payload
    
    And also check the presence of a particular permission in the permissions string
    '''
    
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'forbidden',
            'description': 'Permission not found'
        }, 403)
    return True


def verify_decode_jwt(token):
    '''
    Decode the JWT to get all its fields, and verify it
    
    Author: Udacity Team, Date: 29/09/2022, 
    Title: cd0039-Identity-and-Access-Management
    URL: https://github.com/udacity/cd0039-Identity-and-Access-Management/blob/master/lesson-2-Identity-and-Authentication/BasicFlaskAuth/app.py
    '''

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 403)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator