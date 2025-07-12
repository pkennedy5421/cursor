from twilio.rest import Client
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models

load_dotenv()

# Configure Twilio client
client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

async def send_notification(db: Session, search_result: models.SearchResult):
    """
    Send SMS notification for a new search result
    """
    search_request = search_result.search_request
    user = search_request.user
    
    message = f"""
    New item found matching your search: {search_request.search_query}
    
    Title: {search_result.item_title}
    Description: {search_result.item_description}
    URL: {search_result.item_url}
    """
    
    try:
        client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=user.phone_number
        )
        search_result.is_notified = True
        db.commit()
        return True
    except Exception as e:
        print(f"Failed to send SMS: {str(e)}")
        return False

async def process_notifications(db: Session):
    """
    Process all un-notified search results
    """
    un_notified_results = db.query(models.SearchResult).filter(
        models.SearchResult.is_notified == False
    ).all()
    
    for result in un_notified_results:
        await send_notification(db, result) 