#!/usr/bin/env python3
"""
Script to test and inspect The Outworld Scraper API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_event(event, index):
    """Print event details in a formatted way"""
    print(f"\n📅 EVENT {index + 1}:")
    print(f"  📍 Title: {event['title']}")
    print(f"  📖 Description: {event['description'][:100]}...")
    print(f"  🗓️  Date: {event['date_start']} - {event['date_end']}")
    print(f"  📍 Location: {event['location_name']}")
    print(f"  🏠 Address: {event['address']}, {event['city']}")
    print(f"  🎯 Age Group: {event['age_group']}")
    print(f"  🏷️  Categories: {', '.join(event['categories'])}")
    print(f"  💰 Price: {event['price_type']}")
    print(f"  🔗 Source: {event['source_url']}")
    print(f"  📱 Lat/Lng: {event['latitude']}, {event['longitude']}")

def test_api():
    """Test all API endpoints and show results"""
    
    print_header("🚀 TESTING THE OUTWORLD SCRAPER API")
    
    # Test root endpoint
    print_header("1. Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test events endpoint
    print_header("2. All Events")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events")
        events = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total Events Found: {len(events)}")
        
        for i, event in enumerate(events):
            print_event(event, i)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test status endpoint
    print_header("3. System Status")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events/status")
        status = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total Events: {status['total_events']}")
        print(f"🕒 Last Updated: {status['last_updated']}")
        print(f"🔄 Status: {status['status']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test filtering
    print_header("4. Filtering Tests")
    
    # Filter by age group
    print("\n🎯 Filter by Age Group: 'kid'")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events?age_group=kid")
        events = response.json()
        print(f"✅ Found {len(events)} events for kids")
        for event in events:
            print(f"  - {event['title']} ({event['age_group']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Filter by city
    print("\n🏙️  Filter by City: 'Denver'")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events?city=Denver")
        events = response.json()
        print(f"✅ Found {len(events)} events in Denver")
        for event in events:
            print(f"  - {event['title']} in {event['city']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Filter by category
    print("\n🔬 Filter by Category: 'science'")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events?category=science")
        events = response.json()
        print(f"✅ Found {len(events)} science events")
        for event in events:
            print(f"  - {event['title']} ({', '.join(event['categories'])})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test combined filters
    print("\n🎯 Combined Filter: city=Denver & age_group=toddler")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/events?city=Denver&age_group=toddler")
        events = response.json()
        print(f"✅ Found {len(events)} events for toddlers in Denver")
        for event in events:
            print(f"  - {event['title']} ({event['age_group']} in {event['city']})")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_scraper_info():
    """Show information about the current scraper"""
    print_header("🤖 SCRAPER INFORMATION")
    print("📍 Current Scraper: Macaroni KID Denver (MOCK)")
    print("🔄 Scraping Schedule: At startup (will be every 24h)")
    print("📊 Data Generated: 3 sample events")
    print("🎯 Age Groups: baby, toddler, kid, youth")
    print("🏷️  Categories: reading, science, music, education, etc.")
    print("💰 Price Types: free, paid")
    print("📍 Locations: Denver area with real coordinates")
    print("🔗 Sources: Mock URLs (will be real in production)")

if __name__ == "__main__":
    show_scraper_info()
    test_api()
    
    print_header("🎉 NEXT STEPS")
    print("1. 📖 Visit http://localhost:8000/docs for interactive API docs")
    print("2. 🔍 Check your Supabase dashboard to see the data")
    print("3. 🛠️  Add real scrapers in app/scrapers/")
    print("4. ⏰ Set up scheduling for automatic scraping")
    print("5. 🚀 Deploy to production") 