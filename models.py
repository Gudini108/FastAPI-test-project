"""Database models"""

from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    author = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)


class PostReaction(Base):
    __tablename__ = 'reactions'

    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    reaction = Column(String)

    user = relationship('User', backref='reactions')
    post = relationship('Post', backref='reactions')
