import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Any
from app.models import Event
from datetime import datetime

# Load environment variables
load_dotenv()

class SupabaseHandler:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(self.url, self.key)
    
    def create_events_table(self):
        """Create events table if it doesn't exist"""
        try:
            # This will create the table with the proper schema
            # Note: In a real scenario, you'd want to use migrations
            pass
        except Exception as e:
            print(f"Error creating table: {e}")
    
    def event_exists(self, event: Event) -> bool:
        """Check if an event with the same title, date, and location already exists"""
        try:
            result = self.client.table('events').select('id').eq(
                'title', event.title
            ).eq(
                'date_start', event.date_start.isoformat()
            ).eq(
                'location_name', event.location_name
            ).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking event existence: {e}")
            return False
    
    def insert_event(self, event: Event) -> Dict[str, Any]:
        """Insert a single event into the database if it doesn't already exist"""
        try:
            # Check if event already exists
            if self.event_exists(event):
                print(f"⚠️  Event '{event.title}' already exists, skipping...")
                return None
            
            event_data = event.dict()
            
            # Remove id field if it's None (let Supabase auto-generate it)
            if event_data.get('id') is None:
                event_data.pop('id', None)
            
            # Convert datetime to ISO string for Supabase
            event_data['date_start'] = event_data['date_start'].isoformat()
            event_data['date_end'] = event_data['date_end'].isoformat()
            event_data['last_updated_at'] = event_data['last_updated_at'].isoformat()
            
            result = self.client.table('events').insert(event_data).execute()
            print(f"✅ Event '{event.title}' inserted successfully")
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting event: {e}")
            return None
    
    def clear_all_events(self) -> bool:
        """Clear all events from the database (for testing purposes)"""
        try:
            result = self.client.table('events').delete().neq('id', 0).execute()
            print(f"🗑️  Cleared all events from database")
            return True
        except Exception as e:
            print(f"Error clearing events: {e}")
            return False
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Fetch all events from the database"""
        try:
            result = self.client.table('events').select('*').execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_events_by_filters(self, city: str = None, age_group: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Fetch events with optional filters"""
        try:
            query = self.client.table('events').select('*')
            
            if city:
                query = query.eq('city', city)
            if age_group:
                query = query.eq('age_group', age_group)
            if category:
                query = query.contains('categories', [category])
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching filtered events: {e}")
            return []
    
    def get_events_by_title_and_location(self, title: str, location_name: str) -> List[Dict]:
        """Get events by title and location (for duplicate checking)"""
        try:
            result = self.client.table('events').select('*').eq('title', title).eq('location_name', location_name).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting events by title and location: {e}")
            return []

# Database handler wrapper for consistent API
class DatabaseHandler:
    def __init__(self):
        self.supabase = SupabaseHandler()
    
    def event_exists(self, title: str, date_start, location_name: str) -> bool:
        """Check if an event with the same title, date, and location already exists"""
        try:
            result = self.supabase.client.table('events').select('id').eq(
                'title', title
            ).eq(
                'date_start', date_start.isoformat()
            ).eq(
                'location_name', location_name
            ).execute()
            
            return len(result.data) > 0
        except Exception as e:
            print(f"Error checking event existence: {e}")
            return False
    
    def save_events(self, events: List[Event]) -> bool:
        """Save multiple events to database, avoiding duplicates"""
        try:
            saved_count = 0
            skipped_count = 0
            
            for event in events:
                # More robust duplicate check
                if not self.event_exists(event.title, event.date_start, event.location_name):
                    # Double check by title and location only (in case of minor time differences)
                    existing_events = self.supabase.get_events_by_title_and_location(event.title, event.location_name)
                    if not existing_events:
                        result = self.supabase.insert_event(event)
                        if result:
                            saved_count += 1
                            print(f"✅ Saved event: {event.title}")
                        else:
                            print(f"❌ Failed to save event: {event.title}")
                    else:
                        skipped_count += 1
                        print(f"⏭️  Skipped duplicate: {event.title}")
                else:
                    skipped_count += 1
                    print(f"⏭️  Event already exists: {event.title}")
            
            print(f"📊 Saved {saved_count} new events, skipped {skipped_count} duplicates")
            return True
        except Exception as e:
            print(f"Error saving events: {e}")
            return False
    
    def get_all_events(self) -> List[Event]:
        """Get all events from database as Event objects"""
        try:
            events_data = self.supabase.get_all_events()
            events = []
            
            for event_data in events_data:
                try:
                    # Convert ISO strings back to datetime objects
                    event_data['date_start'] = datetime.fromisoformat(event_data['date_start'].replace('Z', '+00:00'))
                    event_data['date_end'] = datetime.fromisoformat(event_data['date_end'].replace('Z', '+00:00'))
                    event_data['last_updated_at'] = datetime.fromisoformat(event_data['last_updated_at'].replace('Z', '+00:00'))
                    
                    # Convert age_group and price_type back to enums
                    from app.models import AgeGroup, PriceType
                    event_data['age_group'] = AgeGroup(event_data['age_group'])
                    event_data['price_type'] = PriceType(event_data['price_type'])
                    
                    event = Event(**event_data)
                    events.append(event)
                    
                except Exception as e:
                    print(f"Error parsing event data: {e}")
                    continue
            
            return events
        except Exception as e:
            print(f"Error getting all events: {e}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Event:
        """Get a specific event by ID"""
        try:
            result = self.supabase.client.table('events').select('*').eq('id', event_id).execute()
            if result.data:
                event_data = result.data[0]
                # Convert datetime strings and enums (similar to get_all_events)
                from datetime import datetime
                from app.models import AgeGroup, PriceType
                
                event_data['date_start'] = datetime.fromisoformat(event_data['date_start'].replace('Z', '+00:00'))
                event_data['date_end'] = datetime.fromisoformat(event_data['date_end'].replace('Z', '+00:00'))
                event_data['last_updated_at'] = datetime.fromisoformat(event_data['last_updated_at'].replace('Z', '+00:00'))
                event_data['age_group'] = AgeGroup(event_data['age_group'])
                event_data['price_type'] = PriceType(event_data['price_type'])
                
                return Event(**event_data)
            return None
        except Exception as e:
            print(f"Error getting event by ID: {e}")
            return None

    def get_active_events(self) -> List[Event]:
        """Get only active events (not expired)"""
        try:
            current_datetime = datetime.now()
            result = self.supabase.client.table('events').select('*').gte(
                'date_end', current_datetime.isoformat()
            ).execute()
            
            events = []
            for event_data in result.data:
                try:
                    # Convert datetime strings and enums (similar to get_all_events)
                    event_data['date_start'] = datetime.fromisoformat(event_data['date_start'].replace('Z', '+00:00'))
                    event_data['date_end'] = datetime.fromisoformat(event_data['date_end'].replace('Z', '+00:00'))
                    event_data['last_updated_at'] = datetime.fromisoformat(event_data['last_updated_at'].replace('Z', '+00:00'))
                    
                    # Convert age_group and price_type back to enums
                    from app.models import AgeGroup, PriceType
                    event_data['age_group'] = AgeGroup(event_data['age_group'])
                    event_data['price_type'] = PriceType(event_data['price_type'])
                    
                    event = Event(**event_data)
                    events.append(event)
                    
                except Exception as e:
                    print(f"Error parsing event data: {e}")
                    continue
            
            return events
        except Exception as e:
            print(f"Error getting active events: {e}")
            return []
    
    def delete_old_events(self, cutoff_date) -> int:
        """Delete events older than cutoff_date"""
        try:
            result = self.supabase.client.table('events').delete().lt(
                'date_start', cutoff_date.isoformat()
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            return deleted_count
        except Exception as e:
            print(f"Error deleting old events: {e}")
            return 0

    def delete_expired_events(self, current_datetime) -> int:
        """Delete events that have already ended (expired)"""
        try:
            result = self.supabase.client.table('events').delete().lt(
                'date_end', current_datetime.isoformat()
            ).execute()
            
            deleted_count = len(result.data) if result.data else 0
            return deleted_count
        except Exception as e:
            print(f"Error deleting expired events: {e}")
            return 0

    def clear_all_events(self) -> bool:
        """Clear all events from database (for testing/fixing purposes)"""
        return self.supabase.clear_all_events()

# Global instances
db_handler = SupabaseHandler()
database_handler = DatabaseHandler() 