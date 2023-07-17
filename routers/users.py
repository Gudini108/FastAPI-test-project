"""User endpoints and logic"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, APIRouter, Depends

import db.models as models
from db.database import get_db
from base.schemas import User
from utils import get_current_user


router = APIRouter()


@router.get('/users', tags=['Users'])
def get_users(current_user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    """Get list of usernames for authenticated users"""
    if not current_user:
        raise HTTPException(status_code=401, detail='Not authenticated')

    users = db.query(models.User.username).all()
    return [username for username, in users]
