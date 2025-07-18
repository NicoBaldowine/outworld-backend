#!/usr/bin/env python3
"""
Test script for multiple scrapers with mandatory images
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all scrapers
from app.scrapers import macaronikid, denver_events, colorado_parent, denver_recreation
from app.database import DatabaseHandler
from app.scheduler import EventScheduler

def test_scraper_with_images(scraper_name, scraper_module):
    """Test a single scraper and verify all events have images"""
    print(f"\n🕷️  Testing {scraper_name} scraper...")
    
    try:
        # Run the scraper
        events = scraper_module.scrape_events()
        
        if not events:
            print(f"❌ No events found from {scraper_name}")
            return False
        
        print(f"✅ Found {len(events)} events from {scraper_name}")
        
        # Check each event for required fields
        valid_events = 0
        events_with_images = 0
        
        for i, event in enumerate(events, 1):
            print(f"\n📅 Event {i}: {event.title}")
            print(f"   📍 Location: {event.location_name}")
            print(f"   🎯 Age Group: {event.age_group.value}")
            print(f"   🏷️  Categories: {', '.join(event.categories)}")
            print(f"   💰 Price: {event.price_type.value}")
            
            # Check for required fields
            has_title = bool(event.title)
            has_description = bool(event.description)
            has_location = bool(event.location_name)
            has_address = bool(event.address)
            has_image = bool(event.image_url)
            
            print(f"   ✅ Title: {'✓' if has_title else '❌'}")
            print(f"   ✅ Description: {'✓' if has_description else '❌'}")
            print(f"   ✅ Location: {'✓' if has_location else '❌'}")
            print(f"   ✅ Address: {'✓' if has_address else '❌'}")
            print(f"   🖼️  Image URL: {'✓' if has_image else '❌'}")
            
            if has_image:
                print(f"   🔗 Image: {event.image_url}")
                events_with_images += 1
            else:
                print(f"   ⚠️  WARNING: Missing image URL!")
            
            if all([has_title, has_description, has_location, has_address, has_image]):
                valid_events += 1
        
        print(f"\n📊 {scraper_name} Summary:")
        print(f"   Total events: {len(events)}")
        print(f"   Valid events: {valid_events}")
        print(f"   Events with images: {events_with_images}")
        print(f"   Image coverage: {(events_with_images / len(events) * 100):.1f}%")
        
        if events_with_images == len(events):
            print(f"   ✅ All events have images!")
            return True
        else:
            print(f"   ❌ Some events missing images!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {scraper_name}: {e}")
        return False

def test_all_scrapers():
    """Test all scrapers"""
    print("🚀 Testing all scrapers with mandatory images...")
    
    scrapers = {
        'Macaroni KID Denver': macaronikid,
        'Denver.org Events': denver_events,
        'Colorado Parent': colorado_parent,
        'Denver Recreation': denver_recreation
    }
    
    results = {}
    total_events = 0
    
    for scraper_name, scraper_module in scrapers.items():
        success = test_scraper_with_images(scraper_name, scraper_module)
        results[scraper_name] = success
        
        if success:
            events = scraper_module.scrape_events()
            total_events += len(events)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total scrapers tested: {len(scrapers)}")
    print(f"   Successful scrapers: {sum(results.values())}")
    print(f"   Failed scrapers: {len(scrapers) - sum(results.values())}")
    print(f"   Total events with images: {total_events}")
    
    for scraper_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {scraper_name}")
    
    return all(results.values())

async def test_scheduler_integration():
    """Test scheduler integration with multiple scrapers"""
    print("\n🗓️  Testing scheduler integration...")
    
    try:
        # Create scheduler instance
        scheduler = EventScheduler()
        
        # Test scraping all sources
        events = await scheduler.scrape_all_sources()
        
        print(f"✅ Scheduler scraped {len(events)} events from all sources")
        
        # Check image coverage
        events_with_images = sum(1 for event in events if event.image_url)
        image_coverage = (events_with_images / len(events) * 100) if events else 0
        
        print(f"🖼️  Image coverage: {image_coverage:.1f}% ({events_with_images}/{len(events)})")
        
        if image_coverage == 100:
            print("✅ All events have images!")
            return True
        else:
            print("❌ Some events missing images!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scheduler: {e}")
        return False

def test_database_integration():
    """Test database integration"""
    print("\n💾 Testing database integration...")
    
    try:
        db = DatabaseHandler()
        
        # Get all events
        events = db.get_all_events()
        print(f"📊 Found {len(events)} events in database")
        
        if events:
            # Check image coverage in database
            events_with_images = sum(1 for event in events if event.image_url)
            image_coverage = (events_with_images / len(events) * 100)
            
            print(f"🖼️  Database image coverage: {image_coverage:.1f}% ({events_with_images}/{len(events)})")
            
            # Show event breakdown
            age_groups = {}
            categories = {}
            sources = {}
            
            for event in events:
                age_group = event.age_group.value
                age_groups[age_group] = age_groups.get(age_group, 0) + 1
                
                for category in event.categories:
                    categories[category] = categories.get(category, 0) + 1
                
                source = event.source_url.split('/')[2] if event.source_url else 'unknown'
                sources[source] = sources.get(source, 0) + 1
            
            print(f"📊 Age group distribution: {age_groups}")
            print(f"📊 Category distribution: {categories}")
            print(f"📊 Source distribution: {sources}")
            
            return True
        else:
            print("⚠️  No events found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("🧪 TESTING MULTIPLE SCRAPERS WITH MANDATORY IMAGES")
    print("="*60)
    
    # Test individual scrapers
    scrapers_success = test_all_scrapers()
    
    # Test scheduler integration
    scheduler_success = asyncio.run(test_scheduler_integration())
    
    # Test database integration
    database_success = test_database_integration()
    
    print("\n" + "="*60)
    print("🎯 OVERALL TEST RESULTS")
    print("="*60)
    
    print(f"✅ Individual scrapers: {'PASS' if scrapers_success else 'FAIL'}")
    print(f"✅ Scheduler integration: {'PASS' if scheduler_success else 'FAIL'}")
    print(f"✅ Database integration: {'PASS' if database_success else 'FAIL'}")
    
    overall_success = scrapers_success and scheduler_success and database_success
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ All scrapers working with mandatory images")
        print("✅ Scheduler integration working")
        print("✅ Database integration working")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the output above for details.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 