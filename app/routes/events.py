from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from app.database import db_handler
from app.models import EventResponse

router = APIRouter()


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    city: Optional[str] = Query(None, description="Filter by city"),
    age_group: Optional[str] = Query(None, description="Filter by age group (baby, toddler, kid, youth)"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get all events with optional filters
    """
    try:
        if city or age_group or category:
            events = db_handler.get_events_by_filters(city=city, age_group=age_group, category=category)
        else:
            events = db_handler.get_all_events()
        
        # Convert to response models
        response_events = []
        for event in events:
            # Parse datetime strings back to datetime objects
            event['date_start'] = datetime.fromisoformat(event['date_start'].replace('Z', '+00:00'))
            event['date_end'] = datetime.fromisoformat(event['date_end'].replace('Z', '+00:00'))
            event['last_updated_at'] = datetime.fromisoformat(event['last_updated_at'].replace('Z', '+00:00'))
            
            response_events.append(EventResponse(**event))
        
        return response_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@router.get("/events/today", response_model=List[EventResponse])
async def get_today_events():
    """
    Get events happening today
    """
    try:
        all_events = db_handler.get_all_events()
        today = date.today()
        
        today_events = []
        for event in all_events:
            event_date = datetime.fromisoformat(event['date_start'].replace('Z', '+00:00')).date()
            if event_date == today:
                # Parse datetime strings back to datetime objects
                event['date_start'] = datetime.fromisoformat(event['date_start'].replace('Z', '+00:00'))
                event['date_end'] = datetime.fromisoformat(event['date_end'].replace('Z', '+00:00'))
                event['last_updated_at'] = datetime.fromisoformat(event['last_updated_at'].replace('Z', '+00:00'))
                
                today_events.append(EventResponse(**event))
        
        return today_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's events: {str(e)}")


@router.get("/events/status")
async def get_scraping_status():
    """
    Get scraping status and basic stats
    """
    try:
        events = db_handler.get_all_events()
        return {
            "total_events": len(events),
            "last_updated": datetime.now().isoformat(),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}") 