import time
import json
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

class MemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
        self.set_count = 0
        logger.info(f"🗄️  Memory cache initialized with default TTL: {default_ttl}s")
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item is expired"""
        return time.time() > item['expires_at']
    
    def _cleanup_expired(self):
        """Remove expired items from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items() 
            if current_time > item['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired cache items")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        self._cleanup_expired()
        
        if key in self.cache:
            item = self.cache[key]
            if not self._is_expired(item):
                self.hit_count += 1
                logger.debug(f"🎯 Cache HIT for key: {key}")
                return item['value']
            else:
                del self.cache[key]
        
        self.miss_count += 1
        logger.debug(f"❌ Cache MISS for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = time.time() + ttl
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        self.set_count += 1
        logger.debug(f"💾 Cache SET for key: {key}, TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"🗑️  Cache DELETE for key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("🧹 Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        self._cleanup_expired()
        
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_items': len(self.cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'set_count': self.set_count,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests,
            'cache_size_mb': self._get_size_mb(),
            'oldest_item_age_seconds': self._get_oldest_item_age()
        }
    
    def _get_size_mb(self) -> float:
        """Estimate cache size in MB"""
        try:
            cache_str = json.dumps(self.cache, default=str)
            return len(cache_str.encode('utf-8')) / (1024 * 1024)
        except:
            return 0.0
    
    def _get_oldest_item_age(self) -> Optional[float]:
        """Get age of oldest item in seconds"""
        if not self.cache:
            return None
        
        oldest_created_at = min(item['created_at'] for item in self.cache.values())
        return time.time() - oldest_created_at

# Global cache instance
cache = MemoryCache(default_ttl=300)  # 5 minutes default

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(func_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(func_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Cache configuration for different types of data
CACHE_CONFIG = {
    'events': {
        'ttl': 300,  # 5 minutes
        'key_prefix': 'events:'
    },
    'map_data': {
        'ttl': 600,  # 10 minutes
        'key_prefix': 'map:'
    },
    'locations': {
        'ttl': 1800,  # 30 minutes
        'key_prefix': 'locations:'
    },
    'stats': {
        'ttl': 180,  # 3 minutes
        'key_prefix': 'stats:'
    },
    'scheduler': {
        'ttl': 60,  # 1 minute
        'key_prefix': 'scheduler:'
    }
}

def get_cache_config(cache_type: str) -> Dict[str, Any]:
    """Get cache configuration for specific type"""
    return CACHE_CONFIG.get(cache_type, {'ttl': 300, 'key_prefix': ''})

# Cache warming functions
def warm_cache():
    """Warm up cache with frequently accessed data"""
    logger.info("🔥 Starting cache warming...")
    
    try:
        # This would be called during startup to pre-populate cache
        # with frequently accessed data
        pass
        
    except Exception as e:
        logger.error(f"❌ Error warming cache: {e}")

def invalidate_events_cache():
    """Invalidate all events-related cache"""
    logger.info("🗑️  Invalidating events cache...")
    
    keys_to_delete = [
        key for key in cache.cache.keys() 
        if key.startswith('events:') or key.startswith('map:') or key.startswith('stats:')
    ]
    
    for key in keys_to_delete:
        cache.delete(key)
    
    logger.info(f"✅ Invalidated {len(keys_to_delete)} cache keys")

# Cache-aware database operations
class CachedDatabase:
    """Database wrapper with caching"""
    
    def __init__(self, db_handler):
        self.db = db_handler
    
    @cached(ttl=300, key_prefix="db_events:")
    def get_all_events(self):
        """Get all events with caching"""
        logger.debug("🔄 Fetching all events from database (cache miss)")
        return self.db.get_all_events()
    
    @cached(ttl=600, key_prefix="db_event:")
    def get_event_by_id(self, event_id: str):
        """Get event by ID with caching"""
        logger.debug(f"🔄 Fetching event {event_id} from database (cache miss)")
        return self.db.get_event_by_id(event_id)
    
    def save_events(self, events):
        """Save events and invalidate cache"""
        result = self.db.save_events(events)
        invalidate_events_cache()
        return result
    
    def delete_old_events(self, cutoff_date):
        """Delete old events and invalidate cache"""
        result = self.db.delete_old_events(cutoff_date)
        invalidate_events_cache()
        return result

    def delete_expired_events(self, current_datetime):
        """Delete expired events and invalidate cache"""
        result = self.db.delete_expired_events(current_datetime)
        invalidate_events_cache()
        return result

# Health check for cache
def get_cache_health() -> Dict[str, Any]:
    """Get cache health status"""
    stats = cache.get_stats()
    
    # Determine health status
    health_status = "healthy"
    if stats['total_items'] > 1000:  # Too many items
        health_status = "warning"
    elif stats['hit_rate_percent'] < 50 and stats['total_requests'] > 100:  # Low hit rate
        health_status = "warning"
    
    return {
        'status': health_status,
        'statistics': stats,
        'cache_type': 'memory',
        'default_ttl': cache.default_ttl
    } 