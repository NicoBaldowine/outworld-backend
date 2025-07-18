#!/usr/bin/env python3
"""
Script to reset data and re-scrape with duplicate prevention
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db_handler
from app.scrapers.macaronikid import scrape_and_save_events

def reset_and_rescrape():
    """Clear existing data and re-scrape with duplicate prevention"""
    print("🚀 RESETTING THE OUTWORLD SCRAPER DATA")
    print("="*50)
    
    # Step 1: Clear existing data
    print("\n1. 🗑️  Clearing existing events...")
    success = db_handler.clear_all_events()
    if not success:
        print("❌ Failed to clear events")
        return
    
    # Step 2: Re-scrape with duplicate prevention
    print("\n2. 🕷️  Re-scraping events with duplicate prevention...")
    try:
        events = scrape_and_save_events()
        print(f"📊 Generated {len(events)} events")
        
        # Save events to database
        saved_count = 0
        for event in events:
            result = db_handler.insert_event(event)
            if result:
                saved_count += 1
        
        print(f"✅ Successfully saved {saved_count} unique events")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return
    
    # Step 3: Show final stats
    print("\n3. 📊 Final Statistics:")
    all_events = db_handler.get_all_events()
    print(f"📈 Total events in database: {len(all_events)}")
    
    # Show breakdown by age group
    age_groups = {}
    for event in all_events:
        age_group = event['age_group']
        age_groups[age_group] = age_groups.get(age_group, 0) + 1
    
    print("\n👶 Events by Age Group:")
    for age_group, count in age_groups.items():
        print(f"  {age_group}: {count} events")
    
    print("\n🎉 Data reset complete!")
    print("💡 Now restart your API server to see the clean data")

if __name__ == "__main__":
    reset_and_rescrape() 