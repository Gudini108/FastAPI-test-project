"""User signup and login endpoints"""

import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, APIRouter, Depends

import db.models as models
from base.models import UserRegistration
from settings import ACCESS_TOKEN_EXPIRE_MINUTES
from db.database import db_engine, get_db
from utils import (
    hash_password,
    verify_email,
    authenticate_user,
    create_access_token
)


router = APIRouter()

models.Base.metadata.create_all(bind=db_engine)


@router.post('/signup', tags=['Authentication'])
def signup(user: UserRegistration, db: Session = Depends(get_db)):
    """Signup endpoint"""
    username_exists = db.query(models.User).filter(
        func.lower(models.User.username) == func.lower(user.username)).first()
    if username_exists:
        raise HTTPException(status_code=409,
                            detail='This username already taken')

    email_exists = db.query(models.User).filter(
        func.lower(models.User.email) == func.lower(user.email)).first()
    if email_exists:
        raise HTTPException(status_code=409,
                            detail='This email is already taken')

    email_is_verified = verify_email(user.email)
    if not email_is_verified:
        raise HTTPException(status_code=400, detail='Invalid email address')

    hashed_password = hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(
        username=user.username,
        password=user.password,
        email=user.email
    )
    db.add(new_user)
    db.commit()
    return {'message': f'User {user.username} created'}


@router.post('/login', tags=['Authentication'])
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    """Login endpoint"""
    username = form_data.username
    password = form_data.password
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=401,
                            detail='Invalid username or password')

    access_token_expire_time = datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.username},
                                       expires_delta=access_token_expire_time)

    return {'access_token': access_token, 'token_type': 'bearer'}
