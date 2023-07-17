"""Base models"""

from pydantic import BaseModel, EmailStr, Field


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
