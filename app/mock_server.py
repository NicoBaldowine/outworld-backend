#!/usr/bin/env python3
"""
Mock server for quick demo without Supabase
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn

# Create mock events data
mock_events = [
    {
        "id": 1,
        "title": "🎨 Children's Art Workshop",
        "description": "Creative art session for kids to explore colors and shapes. All materials provided!",
        "date_start": (datetime.now() + timedelta(days=1)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "location_name": "Denver Art Museum",
        "address": "100 W 14th Ave Pkwy",
        "city": "Denver",
        "latitude": 39.7372,
        "longitude": -104.9897,
        "age_group": "kid",
        "categories": ["art", "creative"],
        "price_type": "paid",
        "source_url": "https://denverartmuseum.org",
        "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400"
    },
    {
        "id": 2,
        "title": "🦋 Butterfly Garden Tour",
        "description": "Explore the beautiful butterfly conservatory and learn about these amazing creatures!",
        "date_start": (datetime.now() + timedelta(days=2)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
        "location_name": "Denver Botanic Gardens",
        "address": "1007 York St",
        "city": "Denver",
        "latitude": 39.7322,
        "longitude": -104.9603,
        "age_group": "toddler",
        "categories": ["nature", "animals"],
        "price_type": "free",
        "source_url": "https://botanicgardens.org",
        "image_url": "https://images.unsplash.com/photo-1444930694458-01babf71c6ed?w=400"
    },
    {
        "id": 3,
        "title": "🧪 Science Fun Lab",
        "description": "Hands-on science experiments designed for young scientists. Safety equipment provided.",
        "date_start": (datetime.now() + timedelta(days=3)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=3, hours=1.5)).isoformat(),
        "location_name": "Denver Museum of Nature & Science",
        "address": "2001 Colorado Blvd",
        "city": "Denver",
        "latitude": 39.7476,
        "longitude": -104.9426,
        "age_group": "youth",
        "categories": ["science", "education"],
        "price_type": "paid",
        "source_url": "https://dmns.org",
        "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400"
    },
    {
        "id": 4,
        "title": "📚 Story Time Adventure",
        "description": "Interactive storytelling session with songs, crafts, and reading activities.",
        "date_start": (datetime.now() + timedelta(days=4)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=4, hours=1)).isoformat(),
        "location_name": "Denver Public Library",
        "address": "10 W 14th Ave Pkwy",
        "city": "Denver",
        "latitude": 39.7368,
        "longitude": -104.9918,
        "age_group": "baby",
        "categories": ["reading", "education"],
        "price_type": "free",
        "source_url": "https://denverlibrary.org",
        "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400"
    },
    {
        "id": 5,
        "title": "🎪 Mini Circus Show",
        "description": "Amazing circus performance featuring juggling, magic tricks, and acrobatics just for kids!",
        "date_start": (datetime.now() + timedelta(days=5)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=5, hours=2)).isoformat(),
        "location_name": "Red Rocks Park",
        "address": "18300 W Alameda Pkwy",
        "city": "Morrison",
        "latitude": 39.6654,
        "longitude": -105.2055,
        "age_group": "kid",
        "categories": ["entertainment", "outdoor"],
        "price_type": "paid",
        "source_url": "https://redrocksonline.com",
        "image_url": "https://images.unsplash.com/photo-1470217957101-da7150b9b681?w=400"
    },
    {
        "id": 6,
        "title": "🏊‍♀️ Baby Swimming Class",
        "description": "Gentle water introduction for babies with certified instructors. Parent participation required.",
        "date_start": (datetime.now() + timedelta(days=6)).isoformat(),
        "date_end": (datetime.now() + timedelta(days=6, hours=0.5)).isoformat(),
        "location_name": "Denver Recreation Center",
        "address": "1865 Larimer St",
        "city": "Denver",
        "latitude": 39.7508,
        "longitude": -104.9968,
        "age_group": "baby",
        "categories": ["water", "health"],
        "price_type": "paid",
        "source_url": "https://denvergov.org/recreation",
        "image_url": "https://images.unsplash.com/photo-1541411487730-28e3eaf0b01b?w=400"
    }
]

app = FastAPI(title="OutWorld Mock API", description="Demo API with sample events")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🎪 OutWorld Mock API - Demo with Sample Events"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Mock API is running perfectly!",
        "database": {
            "events_count": len(mock_events),
            "status": "connected"
        }
    }

@app.get("/api/v1/events")
async def get_events(
    age_group: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    price_type: Optional[str] = Query(None),
    limit: Optional[int] = Query(12)
):
    """Get events with optional filtering"""
    filtered_events = mock_events.copy()
    
    # Apply filters
    if age_group:
        filtered_events = [e for e in filtered_events if e["age_group"] == age_group]
    
    if category:
        filtered_events = [e for e in filtered_events if category in e["categories"]]
    
    if price_type:
        filtered_events = [e for e in filtered_events if e["price_type"] == price_type]
    
    # Apply limit
    if limit:
        filtered_events = filtered_events[:limit]
    
    return filtered_events

if __name__ == "__main__":
    print("🎪 Starting OutWorld Mock Server...")
    print("🌐 Frontend will be available at: http://localhost:8000")
    print("📊 API docs at: http://localhost:8000/docs")
    uvicorn.run(
        "app.mock_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 