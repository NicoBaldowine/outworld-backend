import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import uvicorn

from app.database import DatabaseHandler
from app.cache import CachedDatabase, get_cache_health, warm_cache, cache
from app.models import Event, AgeGroup, PriceType
from app.routes.maps import router as maps_router
from app.scheduler import (
    start_scheduler, 
    stop_scheduler, 
    run_manual_scraping,
    get_scheduler_status,
    get_next_run_time,
    get_scraping_stats
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database handler with cache
db_handler = DatabaseHandler()
cached_db = CachedDatabase(db_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting The OutWorld Scraper API...")
    
    # Warm up cache
    try:
        warm_cache()
        logger.info("🔥 Cache warmed up successfully")
    except Exception as e:
        logger.error(f"❌ Error warming cache: {e}")
    
    # Start the scheduler
    try:
        await start_scheduler()
        logger.info("✅ Event scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down The OutWorld Scraper API...")
    try:
        await stop_scheduler()
        logger.info("✅ Event scheduler stopped successfully")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")

# Create FastAPI app
app = FastAPI(
    title="The OutWorld Scraper API",
    description="Family events scraper for Colorado (ages 0-10) with maps and caching",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include map routes
app.include_router(maps_router, prefix="/api/v1/maps", tags=["Maps"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with cache information"""
    try:
        # Check database connection
        events = cached_db.get_all_events()
        db_status = "connected"
        
        # Check scheduler status
        scheduler_info = get_scheduler_status()
        scheduler_status = "running" if scheduler_info['running'] else "stopped"
        
        # Check cache health
        cache_health = get_cache_health()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": db_status,
                "events_count": len(events)
            },
            "scheduler": {
                "status": scheduler_status,
                "next_run": get_next_run_time()
            },
            "cache": cache_health,
            "scrapers": {
                "available": scheduler_info.get('scrapers_available', []),
                "total": len(scheduler_info.get('scrapers_available', []))
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Events endpoints
@app.get("/api/v1/events", response_model=List[Event])
async def get_events(
    age_group: Optional[AgeGroup] = Query(None, description="Filter by age group"),
    category: Optional[str] = Query(None, description="Filter by category"),
    price_type: Optional[PriceType] = Query(None, description="Filter by price type"),
    limit: int = Query(50, ge=1, le=100, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip")
):
    """Get all events with optional filtering (cached)"""
    try:
        events = cached_db.get_all_events()
        
        # Apply filters
        if age_group:
            events = [e for e in events if e.age_group == age_group]
        
        if category:
            events = [e for e in events if category.lower() in [c.lower() for c in e.categories]]
        
        if price_type:
            events = [e for e in events if e.price_type == price_type]
        
        # Apply pagination
        total_events = len(events)
        events = events[offset:offset + limit]
        
        logger.info(f"📊 Retrieved {len(events)} events (total: {total_events})")
        return events
        
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Get a specific event by ID (cached)"""
    try:
        event = cached_db.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        logger.info(f"📄 Retrieved event: {event.title}")
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/events/stats")
async def get_events_stats():
    """Get events statistics (cached)"""
    try:
        # Use cache for statistics
        cache_key = "stats:events_stats"
        cached_stats = cache.get(cache_key)
        
        if cached_stats is not None:
            return cached_stats
        
        # Calculate fresh statistics
        events = cached_db.get_all_events()
        
        # Calculate statistics
        total_events = len(events)
        
        # Group by age group
        age_group_stats = {}
        for event in events:
            age_group = event.age_group.value
            age_group_stats[age_group] = age_group_stats.get(age_group, 0) + 1
        
        # Group by category
        category_stats = {}
        for event in events:
            for category in event.categories:
                category_stats[category] = category_stats.get(category, 0) + 1
        
        # Group by price type
        price_type_stats = {}
        for event in events:
            price_type = event.price_type.value
            price_type_stats[price_type] = price_type_stats.get(price_type, 0) + 1
        
        # Group by source
        source_stats = {}
        for event in events:
            source = event.source_url.split('/')[2] if event.source_url else 'unknown'
            source_stats[source] = source_stats.get(source, 0) + 1
        
        # Image statistics
        events_with_images = sum(1 for event in events if event.image_url)
        events_without_images = total_events - events_with_images
        
        # Location statistics
        unique_locations = len(set(f"{event.location_name}|{event.address}" for event in events))
        
        # Date range statistics
        if events:
            dates = [event.date_start for event in events]
            date_range = {
                "earliest": min(dates).isoformat(),
                "latest": max(dates).isoformat()
            }
        else:
            date_range = {"earliest": None, "latest": None}
        
        stats = {
            "total_events": total_events,
            "age_group_distribution": age_group_stats,
            "category_distribution": category_stats,
            "price_type_distribution": price_type_stats,
            "source_distribution": source_stats,
            "image_statistics": {
                "with_images": events_with_images,
                "without_images": events_without_images,
                "image_coverage": (events_with_images / total_events * 100) if total_events > 0 else 0
            },
            "location_statistics": {
                "unique_locations": unique_locations,
                "events_per_location": round(total_events / unique_locations, 2) if unique_locations > 0 else 0
            },
            "date_range": date_range,
            "generated_at": datetime.now().isoformat()
        }
        
        # Cache for 3 minutes
        cache.set(cache_key, stats, ttl=180)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting events stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduler endpoints
@app.get("/api/v1/scheduler/status")
async def get_scheduler_status_endpoint():
    """Get scheduler status and statistics"""
    try:
        status = get_scheduler_status()
        return status
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/scheduler/next-run")
async def get_next_run_endpoint():
    """Get next scheduled run time"""
    try:
        next_run = get_next_run_time()
        return next_run
    except Exception as e:
        logger.error(f"Error getting next run time: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scheduler/run-manual")
async def run_manual_scraping_endpoint():
    """Trigger manual scraping"""
    try:
        logger.info("🔧 Manual scraping triggered via API")
        result = await run_manual_scraping()
        return result
    except Exception as e:
        logger.error(f"Error running manual scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/logs")
async def get_logs():
    """Get scraping logs and statistics"""
    try:
        stats = get_scraping_stats()
        return {
            "logs": {
                "message": "Scraping statistics and logs",
                "timestamp": datetime.now().isoformat()
            },
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        return get_cache_health()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/cache/clear")
async def clear_cache():
    """Clear all cache"""
    try:
        cache.clear()
        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/database/clear")
async def clear_database():
    """Clear all events from database (for fixing URL issues)"""
    try:
        success = db_handler.clear_all_events()
        if success:
            # Also clear cache since it's now outdated
            cache.clear()
            logger.info("🗑️  Database and cache cleared successfully")
            return {
                "message": "Database and cache cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "The OutWorld Scraper API",
        "description": "Family events scraper for Colorado (ages 0-10) with maps and caching",
        "version": "2.0.0",
        "features": {
            "cache": "In-memory caching for improved performance",
            "maps": "Geographic event data with clustering and heatmaps",
            "scrapers": "Multiple data sources for diverse events",
            "scheduler": "Automated daily scraping with cleanup"
        },
        "endpoints": {
            "health": "/health",
            "events": "/api/v1/events",
            "events_stats": "/api/v1/events/stats",
            "scheduler": "/api/v1/scheduler/status",
            "manual_scraping": "/api/v1/scheduler/run-manual",
            "logs": "/api/v1/logs",
            "cache_stats": "/api/v1/cache/stats",
            "maps": "/api/v1/maps/events/map",
            "nearby_events": "/api/v1/maps/events/nearby",
            "location_clusters": "/api/v1/maps/locations/clusters",
            "heatmap": "/api/v1/maps/locations/heatmap"
        },
        "scrapers": {
            "macaronikid": "Macaroni KID Denver",
            "denver_events": "Denver.org Events",
            "colorado_parent": "Colorado Parent Magazine",
            "denver_recreation": "Denver Recreation Centers"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Run the application
if __name__ == "__main__":
    logger.info("🚀 Starting The OutWorld Scraper API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 