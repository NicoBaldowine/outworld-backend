#!/usr/bin/env python3
"""
Find Denver Library events specifically to check if parsing worked
"""
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def find_library_events():
    """Find Denver Library events specifically"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        # Get events from Denver Library specifically
        print("🔍 Looking for Denver Public Library events...")
        result = supabase.table('events').select('*').ilike('location_name', '%library%').execute()
        
        events = result.data
        print(f"✅ Found {len(events)} Denver Library events")
        
        if events:
            print("\n📅 Denver Library Events:")
            for i, event in enumerate(events):
                import pytz
                # Convert from UTC (stored in DB) to Mountain Time (Colorado timezone)
                mountain_tz = pytz.timezone('America/Denver')
                date_start_utc = datetime.fromisoformat(event['date_start'].replace('Z', '+00:00'))
                date_start = date_start_utc.astimezone(mountain_tz)
                
                print(f"{i+1}. {event['title']}")
                print(f"   📍 {event['location_name']}")
                print(f"   🌐 {event['source_url']}")
                print(f"   🗓️  {date_start.strftime('%A, %B %d, %Y')}")
                print(f"   🕐 {date_start.strftime('%I:%M %p')}")
                print()
        else:
            print("❌ No Denver Library events found!")
            
            # Try different search
            result = supabase.table('events').select('*').execute()
            all_events = result.data
            print(f"\n🔍 All {len(all_events)} events:")
            for event in all_events[:10]:
                print(f"- {event['title']} at {event['location_name']}")
                print(f"  Source: {event['source_url']}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False

if __name__ == "__main__":
    print("🔍 FINDING DENVER LIBRARY EVENTS")
    print("="*50)
    find_library_events() 