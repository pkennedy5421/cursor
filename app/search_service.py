import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
import json

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def search_for_item(search_query: str) -> list:
    """
    Use Gemini to search for items matching the query
    Returns a list of dictionaries containing item details
    """
    prompt = f"""
    Search for items matching this description: {search_query}
    Return the results in JSON format with the following structure:
    [
        {{
            "title": "Item title",
            "url": "URL to the item",
            "description": "Brief description of the item"
        }}
    ]
    Only include items that are currently available for purchase.
    """

    response = model.generate_content(prompt)
    try:
        results = json.loads(response.text)
        return results
    except json.JSONDecodeError:
        return []

async def process_search_request(db: Session, search_request: models.SearchRequest):
    """
    Process a search request and store any new results
    """
    results = await search_for_item(search_request.search_query)
    
    for result in results:
        # Check if this result already exists
        existing_result = db.query(models.SearchResult).filter(
            models.SearchResult.search_request_id == search_request.id,
            models.SearchResult.item_url == result["url"]
        ).first()
        
        if not existing_result:
            # Create new search result
            new_result = models.SearchResult(
                search_request_id=search_request.id,
                item_url=result["url"],
                item_title=result["title"],
                item_description=result["description"],
                found_at=datetime.utcnow()
            )
            db.add(new_result)
    
    # Update last checked timestamp
    search_request.last_checked = datetime.utcnow()
    db.commit() 