from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import models, schemas, auth
from .database import engine, get_db
from .search_service import process_search_request
from .sms_service import process_notifications

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Item Search Notifier")
scheduler = AsyncIOScheduler()

# Dependency
async def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/search-requests", response_model=schemas.SearchRequest)
async def create_search_request(
    search_request: schemas.SearchRequestCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_search_request = models.SearchRequest(
        user_id=current_user.id,
        search_query=search_request.search_query
    )
    db.add(db_search_request)
    db.commit()
    db.refresh(db_search_request)
    return db_search_request

@app.get("/search-requests", response_model=list[schemas.SearchRequest])
async def get_search_requests(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SearchRequest).filter(
        models.SearchRequest.user_id == current_user.id
    ).all()

@app.get("/search-requests/{request_id}/results", response_model=list[schemas.SearchResult])
async def get_search_results(
    request_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    search_request = db.query(models.SearchRequest).filter(
        models.SearchRequest.id == request_id,
        models.SearchRequest.user_id == current_user.id
    ).first()
    
    if not search_request:
        raise HTTPException(status_code=404, detail="Search request not found")
    
    return db.query(models.SearchResult).filter(
        models.SearchResult.search_request_id == request_id
    ).all()

async def scheduled_search():
    """
    Scheduled task to process all active search requests
    """
    db = next(get_db())
    try:
        active_requests = db.query(models.SearchRequest).filter(
            models.SearchRequest.is_active == True
        ).all()
        
        for request in active_requests:
            await process_search_request(db, request)
        
        await process_notifications(db)
    finally:
        db.close()

# Start the scheduler when the application starts
@app.on_event("startup")
async def startup_event():
    # Schedule the search task to run daily at midnight
    scheduler.add_job(
        scheduled_search,
        CronTrigger(hour=0, minute=0),
        id="daily_search",
        replace_existing=True
    )
    scheduler.start()

# Stop the scheduler when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown() 