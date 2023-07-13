"""Verification and authentication configurations"""

import jwt
import requests
import datetime
from datetime import datetime as dtime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, Depends

import models
from database import get_db
from settings import (
    EHUNT_ENDPOINT_WEB,
    EHUNT_ENDPOINT_API,
    SECRET_KEY,
    PASSWORD_ENCODING_ALGORITHM,
    OAUTH2_SCHEME
)


password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(input_password, hashed_password):
    """Verifies input password with its stored hashed version in DB"""
    return password_context.verify(input_password, hashed_password)


def hash_password(password):
    """Makes a hash of a password"""
    return password_context.hash(password)


def verify_email(email: str):
    """Verifies input email via emailhunter.co"""
    endpoint = EHUNT_ENDPOINT_WEB + email + EHUNT_ENDPOINT_API
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()['data']
        if data['result'] == 'deliverable':
            return True
    return False


def authenticate_user(username: str, password: str,
                      db: Session = Depends(get_db)):
    """Checks is user is in DB and verifies its password"""
    user = db.query(models.User).filter(
        models.User.username == username).first()
    if user and verify_password(password, user.password):
        return user
    return None


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    """Generates a JWT-access-token"""
    encode_data = data.copy()
    expire_time = dtime.utcnow() + expires_delta
    encode_data.update({'exp': expire_time})
    encoded_jwt = jwt.encode(encode_data, SECRET_KEY,
                             algorithm=PASSWORD_ENCODING_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(OAUTH2_SCHEME),
                     db: Session = Depends(get_db)):
    '''Verifies user's JWT-access-token and checks if user is in DB'''
    try:
        payload = jwt.decode(token, SECRET_KEY,
                             algorithms=[PASSWORD_ENCODING_ALGORITHM])
        username: str = payload.get('sub')

        if username is None:
            raise HTTPException(status_code=401,
                                detail='Invalid authentication credentials')

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

    user = db.query(models.User).filter(
        models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')

    return user
