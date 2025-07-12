from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    phone_number: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class SearchRequestBase(BaseModel):
    search_query: str

class SearchRequestCreate(SearchRequestBase):
    pass

class SearchRequest(SearchRequestBase):
    id: int
    user_id: int
    created_at: datetime
    last_checked: datetime
    is_active: bool

    class Config:
        from_attributes = True

class SearchResultBase(BaseModel):
    item_url: str
    item_title: str
    item_description: str

class SearchResult(SearchResultBase):
    id: int
    search_request_id: int
    found_at: datetime
    is_notified: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 