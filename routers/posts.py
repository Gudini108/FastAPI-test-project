"""Post create, delete and update/edit endpoints"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter

import db.models as models
from base.models import User, PostCreate, PostUpdate
from db.database import get_db
from utils import get_current_user


router = APIRouter()


@router.get('/posts', tags=['Posts'])
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


@router.post('/posts', tags=['Posts'])
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


@router.put('/posts/{post_id}', tags=['Posts'])
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


@router.delete('/posts/{post_id}', tags=['Posts'])
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
