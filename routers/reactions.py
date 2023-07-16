"""Logic and endpoints for liking and disliking a post"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter

import db.models as models
from base.models import User
from db.database import get_db
from utils import get_current_user


router = APIRouter()


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

    reaction_type = 'Like' if is_positive else 'Dislike'

    if post.author_id == user.id:
        raise HTTPException(
            status_code=403,
            detail=f'Cannot {reaction_type.lower()} your own posts')

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


@router.post('/posts/{post_id}/like', tags=['Posts', 'Reactions'])
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


@router.delete('/posts/{post_id}/like', tags=['Posts', 'Reactions'])
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


@router.post('/posts/{post_id}/dislike', tags=['Posts', 'Reactions'])
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


@router.delete('/posts/{post_id}/dislike', tags=['Posts', 'Reactions'])
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
