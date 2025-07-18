from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.database import DatabaseHandler
from app.models import Event, AgeGroup, PriceType
import math

router = APIRouter()
db = DatabaseHandler()

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

@router.get("/events/map")
async def get_events_for_map(
    lat: Optional[float] = Query(None, description="User latitude for distance calculation"),
    lon: Optional[float] = Query(None, description="User longitude for distance calculation"),
    radius: Optional[float] = Query(None, description="Search radius in kilometers"),
    age_group: Optional[AgeGroup] = Query(None, description="Filter by age group"),
    category: Optional[str] = Query(None, description="Filter by category"),
    price_type: Optional[PriceType] = Query(None, description="Filter by price type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of events")
):
    """Get events with location data for map display"""
    try:
        events = db.get_all_events()
        
        # Apply filters
        if age_group:
            events = [e for e in events if e.age_group == age_group]
        
        if category:
            events = [e for e in events if category.lower() in [c.lower() for c in e.categories]]
        
        if price_type:
            events = [e for e in events if e.price_type == price_type]
        
        # Calculate distances if user location provided
        events_with_distance = []
        if lat is not None and lon is not None:
            for event in events:
                distance = calculate_distance(lat, lon, event.latitude, event.longitude)
                events_with_distance.append((event, distance))
            
            # Filter by radius if specified
            if radius is not None:
                events_with_distance = [(e, d) for e, d in events_with_distance if d <= radius]
            
            # Sort by distance
            events_with_distance.sort(key=lambda x: x[1])
            events = [e for e, d in events_with_distance]
        else:
            events_with_distance = [(event, None) for event in events]
        
        # Limit results
        events = events[:limit]
        
        # Format for map display
        map_events = []
        for i, event in enumerate(events):
            event_data = {
                "id": event.id,
                "title": event.title,
                "description": event.description[:200] + "..." if len(event.description) > 200 else event.description,
                "location": {
                    "name": event.location_name,
                    "address": event.address,
                    "city": event.city,
                    "coordinates": {
                        "latitude": event.latitude,
                        "longitude": event.longitude
                    }
                },
                "event_details": {
                    "date_start": event.date_start.isoformat(),
                    "date_end": event.date_end.isoformat(),
                    "age_group": event.age_group.value,
                    "categories": event.categories,
                    "price_type": event.price_type.value,
                    "image_url": event.image_url,
                    "source_url": event.source_url
                }
            }
            
            # Add distance if calculated
            if lat is not None and lon is not None and i < len(events_with_distance):
                distance = events_with_distance[i][1] if events_with_distance[i][1] is not None else calculate_distance(lat, lon, event.latitude, event.longitude)
                event_data["distance_km"] = round(distance, 2)
            
            map_events.append(event_data)
        
        return {
            "events": map_events,
            "total_count": len(map_events),
            "user_location": {
                "latitude": lat,
                "longitude": lon
            } if lat is not None and lon is not None else None,
            "search_radius_km": radius,
            "filters_applied": {
                "age_group": age_group.value if age_group else None,
                "category": category,
                "price_type": price_type.value if price_type else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting map events: {str(e)}")

@router.get("/events/nearby")
async def get_nearby_events(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius: float = Query(10, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of events")
):
    """Get events near a specific location"""
    try:
        events = db.get_all_events()
        
        # Calculate distances and filter by radius
        nearby_events = []
        for event in events:
            distance = calculate_distance(lat, lon, event.latitude, event.longitude)
            if distance <= radius:
                nearby_events.append((event, distance))
        
        # Sort by distance
        nearby_events.sort(key=lambda x: x[1])
        
        # Limit results
        nearby_events = nearby_events[:limit]
        
        # Format response
        result = []
        for event, distance in nearby_events:
            result.append({
                "id": event.id,
                "title": event.title,
                "location_name": event.location_name,
                "address": event.address,
                "distance_km": round(distance, 2),
                "date_start": event.date_start.isoformat(),
                "age_group": event.age_group.value,
                "categories": event.categories,
                "price_type": event.price_type.value,
                "image_url": event.image_url,
                "coordinates": {
                    "latitude": event.latitude,
                    "longitude": event.longitude
                }
            })
        
        return {
            "nearby_events": result,
            "search_center": {
                "latitude": lat,
                "longitude": lon
            },
            "search_radius_km": radius,
            "found_count": len(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting nearby events: {str(e)}")

@router.get("/locations/clusters")
async def get_location_clusters(
    zoom_level: int = Query(10, ge=1, le=18, description="Map zoom level for clustering"),
    bounds: Optional[str] = Query(None, description="Map bounds as 'lat1,lon1,lat2,lon2'")
):
    """Get clustered locations for map display"""
    try:
        events = db.get_all_events()
        
        # Parse bounds if provided
        if bounds:
            try:
                lat1, lon1, lat2, lon2 = map(float, bounds.split(','))
                events = [e for e in events if lat1 <= e.latitude <= lat2 and lon1 <= e.longitude <= lon2]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bounds format. Use 'lat1,lon1,lat2,lon2'")
        
        # Simple clustering based on proximity
        cluster_distance = max(0.5, 20 / zoom_level)  # Adaptive clustering based on zoom
        clusters = []
        processed = set()
        
        for i, event in enumerate(events):
            if i in processed:
                continue
                
            # Create new cluster
            cluster = {
                "center": {
                    "latitude": event.latitude,
                    "longitude": event.longitude
                },
                "events": [event],
                "count": 1
            }
            
            # Find nearby events to add to cluster
            for j, other_event in enumerate(events):
                if i != j and j not in processed:
                    distance = calculate_distance(event.latitude, event.longitude, 
                                                other_event.latitude, other_event.longitude)
                    if distance <= cluster_distance:
                        cluster["events"].append(other_event)
                        cluster["count"] += 1
                        processed.add(j)
            
            processed.add(i)
            clusters.append(cluster)
        
        # Format clusters for response
        formatted_clusters = []
        for cluster in clusters:
            if cluster["count"] == 1:
                # Single event
                event = cluster["events"][0]
                formatted_clusters.append({
                    "type": "single",
                    "coordinates": {
                        "latitude": event.latitude,
                        "longitude": event.longitude
                    },
                    "count": 1,
                    "event": {
                        "id": event.id,
                        "title": event.title,
                        "location_name": event.location_name,
                        "address": event.address,
                        "age_group": event.age_group.value,
                        "price_type": event.price_type.value,
                        "image_url": event.image_url,
                        "date_start": event.date_start.isoformat()
                    }
                })
            else:
                # Multiple events cluster
                avg_lat = sum(e.latitude for e in cluster["events"]) / len(cluster["events"])
                avg_lon = sum(e.longitude for e in cluster["events"]) / len(cluster["events"])
                
                formatted_clusters.append({
                    "type": "cluster",
                    "coordinates": {
                        "latitude": avg_lat,
                        "longitude": avg_lon
                    },
                    "count": cluster["count"],
                    "events": [
                        {
                            "id": e.id,
                            "title": e.title,
                            "location_name": e.location_name,
                            "age_group": e.age_group.value,
                            "date_start": e.date_start.isoformat()
                        } for e in cluster["events"]
                    ]
                })
        
        return {
            "clusters": formatted_clusters,
            "total_clusters": len(formatted_clusters),
            "total_events": len(events),
            "zoom_level": zoom_level,
            "bounds": bounds
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting location clusters: {str(e)}")

@router.get("/locations/heatmap")
async def get_location_heatmap(
    age_group: Optional[AgeGroup] = Query(None, description="Filter by age group"),
    category: Optional[str] = Query(None, description="Filter by category"),
    price_type: Optional[PriceType] = Query(None, description="Filter by price type")
):
    """Get heatmap data for event locations"""
    try:
        events = db.get_all_events()
        
        # Apply filters
        if age_group:
            events = [e for e in events if e.age_group == age_group]
        
        if category:
            events = [e for e in events if category.lower() in [c.lower() for c in e.categories]]
        
        if price_type:
            events = [e for e in events if e.price_type == price_type]
        
        # Create heatmap points
        heatmap_points = []
        location_counts = {}
        
        for event in events:
            coord_key = f"{event.latitude},{event.longitude}"
            if coord_key in location_counts:
                location_counts[coord_key] += 1
            else:
                location_counts[coord_key] = 1
        
        # Format for heatmap
        for coord_key, count in location_counts.items():
            lat, lon = map(float, coord_key.split(','))
            heatmap_points.append({
                "latitude": lat,
                "longitude": lon,
                "weight": count,
                "intensity": min(count / 5.0, 1.0)  # Normalize intensity
            })
        
        return {
            "heatmap_points": heatmap_points,
            "total_points": len(heatmap_points),
            "total_events": len(events),
            "filters_applied": {
                "age_group": age_group.value if age_group else None,
                "category": category,
                "price_type": price_type.value if price_type else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting heatmap data: {str(e)}")

@router.get("/locations/popular")
async def get_popular_locations(
    limit: int = Query(10, ge=1, le=50, description="Number of popular locations to return")
):
    """Get most popular event locations"""
    try:
        events = db.get_all_events()
        
        # Count events per location
        location_counts = {}
        location_details = {}
        
        for event in events:
            location_key = f"{event.location_name}|{event.address}"
            
            if location_key in location_counts:
                location_counts[location_key] += 1
            else:
                location_counts[location_key] = 1
                location_details[location_key] = {
                    "name": event.location_name,
                    "address": event.address,
                    "city": event.city,
                    "coordinates": {
                        "latitude": event.latitude,
                        "longitude": event.longitude
                    }
                }
        
        # Sort by popularity
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Format response
        popular_locations = []
        for i, (location_key, count) in enumerate(sorted_locations[:limit]):
            details = location_details[location_key]
            popular_locations.append({
                "rank": i + 1,
                "location": details,
                "event_count": count,
                "popularity_score": count / len(events) * 100  # Percentage of total events
            })
        
        return {
            "popular_locations": popular_locations,
            "total_locations": len(location_counts),
            "total_events": len(events)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting popular locations: {str(e)}")

@router.get("/denver-bounds")
async def get_denver_bounds():
    """Get Denver area bounds for map initialization"""
    return {
        "bounds": {
            "northeast": {
                "latitude": 39.9142,
                "longitude": -104.6000
            },
            "southwest": {
                "latitude": 39.5501,
                "longitude": -105.1178
            }
        },
        "center": {
            "latitude": 39.7392,
            "longitude": -104.9903
        },
        "zoom_level": 11
    } 