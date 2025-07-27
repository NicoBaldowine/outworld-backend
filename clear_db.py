#!/usr/bin/env python3
"""
Script to clear incorrect events from database
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clear_events():
    """Clear all events from database"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        # Delete all events
        print("🗑️  Clearing all events from database...")
        result = supabase.table('events').delete().neq('id', 0).execute()
        
        print(f"✅ Cleared {len(result.data)} events from database")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing events: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CLEARING INCORRECT EVENTS")
    print("="*50)
    clear_events()
    print("✅ Database cleared! Now restart server to scrape with correct dates.") 