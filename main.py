"""Routing and endpoints"""

import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

import models
from settings import ACCESS_TOKEN_EXPIRE_MINUTES
from database import db_engine, get_db
from utils import (
    hash_password,
    verify_email,
    authenticate_user,
    create_access_token,
    get_current_user
)


API_DESCRIPTION = """
Simple RESTful API using FastAPI for a social networking application

## Functions

* **Signup as a new user**
* **Login as a registered user and obtain JWT-token**
* **Create, Delete, Edit and View Posts**
* **Like and Dislike other user's Posts**
"""

app = FastAPI(
    title='Webtronics FastAPI test project',
    description=API_DESCRIPTION,
    version='1.0.0'
)
router = APIRouter()
templates = Jinja2Templates(directory='templates')

models.Base.metadata.create_all(bind=db_engine)


class User(BaseModel):
    """User model"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserRegistration(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    email: EmailStr


class PostCreate(BaseModel):
    """Model for creating a post"""
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    author: str = Field('Unknown', min_length=1)


class PostUpdate(BaseModel):
    """Model for updating a post"""
    title: str = Field(None, min_length=1)
    content: str = Field(None, min_length=1)
    author: str = Field('Unknown', min_length=1)


@app.get('/', tags=['Root'])
def root():
    """Root endpoint with links to /signup, /login and /posts"""
    return {
        'signup': app.url_path_for('signup'),
        'login': app.url_path_for('login'),
        'posts': app.url_path_for('get_posts')
    }


app.include_router(router, prefix='')


@app.post('/signup', tags=['Authentication'])
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


@app.post('/login', tags=['Authentication'])
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


@app.get('/posts', tags=['Posts'])
def get_posts(db: Session = Depends(get_db)):
    """Get list of all posts with reaction counts"""
    posts_with_reactions = (
        db.query(
            models.Post,
            func.sum(func.cast(
                models.PostReaction.is_positive,
                models.Integer)).label('likes_count'),
            func.sum(func.cast(
                ~models.PostReaction.is_positive,
                models.Integer)).label('dislikes_count')
        )
        .outerjoin(models.Post.reactions)
        .group_by(models.Post.id)
        .all()
    )

    posts_with_counts = [
        {
            'post': post,
            'likes_count': likes_count or 0,
            'dislikes_count': dislikes_count or 0
        }
        for post, likes_count, dislikes_count in posts_with_reactions
    ]

    return posts_with_counts


@app.post('/posts', tags=['Posts'])
def create_post(
    post: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint for creating posts for authorized users"""
    new_post = models.Post(
        author_id=user.id,
        title=post.title,
        content=post.content,
        reactions=[]
    )
    db.add(new_post)
    db.commit()
    return {'message': 'Post created'}


@app.put('/posts/{post_id}', tags=['Posts'])
def update_post(
    post_id: int,
    post: PostUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to update post's fields"""
    post_to_update = db.query(models.Post).filter(
        models.Post.id == post_id,
    ).first()

    if not post_to_update:
        raise HTTPException(status_code=404,
                            detail='Post not found or user unauthorized')

    if post_to_update.author_id == user.id:
        raise HTTPException(status_code=403,
                            detail='User not authorized to update this post')

    for field, value in post.dict(exclude_unset=True).items():
        setattr(post_to_update, field, value)
    db.commit()
    return {'message': 'Post updated'}


@app.delete('/posts/{post_id}', tags=['Posts'])
def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to delete a post by ID"""
    post_to_delete = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.author_id == user.id
    ).first()

    # FIXME: do we also need to delete all reactions linked to the post?

    if post_to_delete:
        db.delete(post_to_delete)
        db.commit()
        return {'message': 'Post deleted'}

    raise HTTPException(status_code=404,
                        detail='Post not found or user is unauthorized')


def handle_reaction(
    is_add: bool,
    is_positive: bool,
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Function to handle likes and dislikes"""
    post = db.query(models.Post).get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')

    if post.author_id == user.id:
        raise HTTPException(status_code=403,
                            detail='Cannot like your own post')

    reaction_type = 'Like' if is_positive else 'Dislike'

    stored_reaction = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.user_id == user.id
    ).first()

    if is_add:
        if stored_reaction:
            if stored_reaction.is_positive != is_positive:
                # Update the existing reaction
                stored_reaction.is_positive = is_positive
                db.commit()
                return {'message': f'Reaction updated to {reaction_type}'}
            else:
                return {'message': f'{reaction_type} already added'}
        else:
            new_reaction = models.PostReaction(
                post_id=post_id,
                user_id=user.id,
                is_positive=is_positive
            )
            db.add(new_reaction)
            db.commit()
            return {'message': f'{reaction_type} added'}

    else:  # is_remove
        if not stored_reaction:
            return {'message': f'{reaction_type} not found'}
        if stored_reaction.is_positive == is_positive:
            db.delete(stored_reaction)
            db.commit()
            return {'message': f'{reaction_type} removed'}
        else:
            return {'message': f'{reaction_type} already removed'}


@app.post('/posts/{post_id}/like', tags=['Posts', 'Reactions'])
def like_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to add likes"""
    return handle_reaction(
        is_add=True,
        is_positive=True,
        post_id=post_id,
        user=user, db=db
    )


@app.delete('/posts/{post_id}/like', tags=['Posts', 'Reactions'])
def remove_like_for_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to remove likes"""
    return handle_reaction(
        is_add=False,
        is_positive=True,
        post_id=post_id,
        user=user, db=db
    )


@app.post('/posts/{post_id}/dislike', tags=['Posts', 'Reactions'])
def dislike_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to add dislikes"""
    return handle_reaction(is_add=True,
                           is_positive=False,
                           post_id=post_id,
                           user=user, db=db
                           )


@app.delete('/posts/{post_id}/dislike', tags=['Posts', 'Reactions'])
def remove_dislike_for_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint to remove dislikes"""
    return handle_reaction(is_add=False,
                           is_positive=False,
                           post_id=post_id,
                           user=user,
                           db=db
                           )


# TODO: add redis cache for likes and dislikes

# @app.on_event('startup')
# async def startup():
#     redis = aioredis.from_url('redis://localhost')
#     FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
