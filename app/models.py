from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    search_requests = relationship("SearchRequest", back_populates="user")

class SearchRequest(Base):
    __tablename__ = "search_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    search_query = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="search_requests")
    results = relationship("SearchResult", back_populates="search_request")

class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(Integer, primary_key=True, index=True)
    search_request_id = Column(Integer, ForeignKey("search_requests.id"))
    item_url = Column(String)
    item_title = Column(String)
    item_description = Column(Text)
    found_at = Column(DateTime, default=datetime.utcnow)
    is_notified = Column(Boolean, default=False)
    search_request = relationship("SearchRequest", back_populates="results") 