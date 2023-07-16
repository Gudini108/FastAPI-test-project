"""Database models"""

from db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String)
    password = Column(String)
    email = Column(String)

    posts = relationship('Post', back_populates='author')
    reactions = relationship('PostReaction', back_populates='user')


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    content = Column(String)

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship('User', back_populates='posts')

    reactions = relationship('PostReaction', cascade='all, delete',
                             back_populates='post')


class PostReaction(Base):
    __tablename__ = 'reactions'
    id = Column(Integer, primary_key=True, index=True)

    is_positive = Column(Boolean)

    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship('Post', back_populates='reactions')

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship('User', back_populates='reactions')
