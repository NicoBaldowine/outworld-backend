import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List
import logging
import re
from app.models import Event, AgeGroup, PriceType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AllTrailsScraper:
    def __init__(self):
        self.base_url = "https://www.alltrails.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Denver area trail locations
        self.denver_locations = [
            {
                "name": "Red Rocks Park",
                "coordinates": (39.6654, -105.2057),
                "city": "Morrison"
            },
            {
                "name": "Golden Gate Canyon State Park", 
                "coordinates": (39.8358, -105.4103),
                "city": "Golden"
            },
            {
                "name": "Mount Falcon Park",
                "coordinates": (39.6407, -105.1893),
                "city": "Morrison"
            },
            {
                "name": "Chatfield State Park",
                "coordinates": (39.5311, -105.0764),
                "city": "Littleton"
            },
            {
                "name": "Bear Creek Lake Park",
                "coordinates": (39.6533, -105.0764),
                "city": "Lakewood"
            }
        ]
    
    def scrape_events(self) -> List[Event]:
        """Scrape family-friendly hiking trails from AllTrails Denver area"""
        logger.info("🥾 Starting AllTrails scraping for family-friendly hiking trails...")
        
        events = []
        
        try:
            # Try to get real trails from AllTrails
            trails = self._get_denver_trails()
            
            # Create events for each trail
            for trail in trails:
                trail_events = self._create_trail_events(trail)
                events.extend(trail_events)
            
            # Add curated trails if we don't have enough
            if len(events) < 8:
                curated_events = self._get_curated_trails()
                events.extend(curated_events)
            
            logger.info(f"🏔️ Successfully found {len(events)} hiking trail events")
            return events[:12]  # Limit to 12 events
            
        except Exception as e:
            logger.error(f"❌ Error scraping AllTrails: {e}")
            return self._get_curated_trails()
    
    def _get_denver_trails(self) -> List[dict]:
        """Get hiking trails from AllTrails Denver area"""
        trails = []
        
        try:
            # Try to scrape AllTrails Denver area
            url = f"{self.base_url}/explore?b_tl_lat=40.0&b_tl_lng=-105.5&b_br_lat=39.5&b_br_lng=-104.5"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for trail elements (this would need adjustment based on actual HTML structure)
                trail_elements = soup.find_all(['div', 'article'], class_=lambda x: x and ('trail' in x.lower()))
                
                for element in trail_elements[:8]:
                    trail = self._extract_trail_info(element)
                    if trail and self._is_family_friendly(trail):
                        trails.append(trail)
                        
        except Exception as e:
            logger.warning(f"Could not scrape AllTrails: {e}")
        
        return trails
    
    def _extract_trail_info(self, element: BeautifulSoup) -> dict:
        """Extract trail information from HTML element"""
        try:
            # Extract trail name
            name_elem = element.find(['h3', 'h2', 'a'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['title', 'name', 'trail']))
            name = name_elem.get_text(strip=True) if name_elem else "Trail"
            
            # Extract difficulty and distance (would need adjustment based on actual structure)
            difficulty_elem = element.find(text=re.compile(r'(Easy|Moderate|Hard)', re.I))
            difficulty = difficulty_elem.strip() if difficulty_elem else "Moderate"
            
            # Extract distance
            distance_elem = element.find(text=re.compile(r'\d+\.?\d*\s*(mi|miles|km)', re.I))
            distance = distance_elem.strip() if distance_elem else "2.5 miles"
            
            return {
                'name': name,
                'difficulty': difficulty,
                'distance': distance,
                'url': f"{self.base_url}/trail/{name.lower().replace(' ', '-')}",
                'real_url': self._get_real_trail_url(name)
            }
            
        except Exception as e:
            logger.error(f"Error extracting trail info: {e}")
            return None
    
    def _is_family_friendly(self, trail: dict) -> bool:
        """Check if trail is family-friendly"""
        difficulty = trail.get('difficulty', '').lower()
        return difficulty in ['easy', 'moderate']
    
    def _get_real_trail_url(self, trail_name: str) -> str:
        """Get real URLs for known Denver area trails"""
        trail_urls = {
            'red rocks trading post trail': 'https://www.redrocksonline.com/explore-red-rocks/trading-post/',
            'castlewood canyon dam trail': 'https://cpw.state.co.us/placestogo/parks/CastlewoodCanyon',
            'bear creek trail': 'https://www.lakewood.org/Government/Departments/Community-Resources/Parks-Forestry-and-Open-Space/Parks-and-Trails/Bear-Creek-Lake-Park',
            'white ranch loop': 'https://www.jeffco.us/1453/White-Ranch-Park',
            'chatfield reservoir trail': 'https://cpw.state.co.us/placestogo/parks/Chatfield',
            'mount falcon trail': 'https://www.jeffco.us/1448/Mount-Falcon-Park',
            'golden gate canyon trail': 'https://cpw.state.co.us/placestogo/parks/GoldenGateCanyon'
        }
        
        # Normalize trail name for lookup
        normalized_name = trail_name.lower().strip()
        
        # Return real URL if we have it, otherwise fallback to a general hiking resource
        return trail_urls.get(normalized_name, 'https://www.alltrails.com/us/colorado/denver')
    
    def _create_trail_events(self, trail: dict) -> List[Event]:
        """Create hiking events for different days"""
        events = []
        
        # Create events for weekends (when families typically hike)
        now = datetime.now()
        
        # Next 3 weekends
        for week_offset in range(3):
            # Saturday and Sunday
            for day_offset in [5, 6]:  # Saturday=5, Sunday=6 (Monday=0)
                event_date = now + timedelta(days=(day_offset - now.weekday() + week_offset * 7))
                
                # Skip past dates
                if event_date < now:
                    continue
                
                # Morning hike time
                event_datetime = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
                
                try:
                    # Select a location for this trail
                    location = self.denver_locations[hash(trail['name']) % len(self.denver_locations)]
                    
                    event = Event(
                        title=f"{trail['name']} - Family Hiking",
                        description=f"Explore {trail['name']} on this family-friendly {trail['difficulty'].lower()} trail. Distance: {trail['distance']}. Perfect for families looking to enjoy nature and outdoor activities together. Bring water, snacks, and comfortable hiking shoes.",
                        date_start=event_datetime,
                        date_end=event_datetime + timedelta(hours=3),  # 3 hour hike
                        location_name=location['name'],
                        address=f"{location['name']}, {location['city']}, CO",
                        city=location['city'],
                        latitude=location['coordinates'][0],
                        longitude=location['coordinates'][1],
                        age_group=self._get_age_group_from_difficulty(trail['difficulty']),
                        categories=["outdoor", "hiking", "nature", "family", "exercise"],
                        price_type=PriceType.FREE,
                        source_url=trail.get('real_url', trail.get('url', self._get_real_trail_url(trail['name']))),
                        image_url=f"https://picsum.photos/400/300?random=trail{hash(trail['name']) % 1000}"
                    )
                    
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error creating trail event: {e}")
                    continue
        
        return events[:2]  # Limit to 2 events per trail
    
    def _get_age_group_from_difficulty(self, difficulty: str) -> AgeGroup:
        """Map trail difficulty to age group"""
        difficulty = difficulty.lower()
        if difficulty == 'easy':
            return AgeGroup.KID
        elif difficulty == 'moderate':
            return AgeGroup.FAMILY
        else:
            return AgeGroup.ADULT
    
    def _get_curated_trails(self) -> List[Event]:
        """High-quality curated family trails for Denver area"""
        now = datetime.now()
        
        curated_trails = [
            {
                'name': 'Red Rocks Trading Post Trail',
                'difficulty': 'Easy',
                'distance': '1.4 miles',
                'location': 'Red Rocks Park',
                'description': 'Easy paved trail perfect for families with stunning red rock formations and views.',
                'real_url': 'https://www.redrocksonline.com/explore-red-rocks/trading-post/'
            },
            {
                'name': 'Castlewood Canyon Dam Trail',
                'difficulty': 'Easy', 
                'distance': '1.0 miles',
                'location': 'Castlewood Canyon State Park',
                'description': 'Short family-friendly trail to historic dam ruins with beautiful canyon views.',
                'real_url': 'https://cpw.state.co.us/placestogo/parks/CastlewoodCanyon'
            },
            {
                'name': 'Bear Creek Trail',
                'difficulty': 'Easy',
                'distance': '2.2 miles',
                'location': 'Bear Creek Lake Park',
                'description': 'Flat, easy trail around the lake perfect for families with young children.',
                'real_url': 'https://www.lakewood.org/Government/Departments/Community-Resources/Parks-Forestry-and-Open-Space/Parks-and-Trails/Bear-Creek-Lake-Park'
            },
            {
                'name': 'White Ranch Loop',
                'difficulty': 'Moderate',
                'distance': '2.8 miles',
                'location': 'White Ranch Park',
                'description': 'Moderate family hike with prairie views and wildlife spotting opportunities.',
                'real_url': 'https://www.jeffco.us/1453/White-Ranch-Park'
            },
            {
                'name': 'Chatfield Reservoir Trail',
                'difficulty': 'Easy',
                'distance': '3.1 miles',
                'location': 'Chatfield State Park',
                'description': 'Easy lakeside trail perfect for families, with opportunities to see waterfowl.',
                'real_url': 'https://cpw.state.co.us/placestogo/parks/Chatfield'
            }
        ]
        
        events = []
        
        for trail in curated_trails:
            # Find matching location
            location = next((loc for loc in self.denver_locations if trail['location'] in loc['name']), self.denver_locations[0])
            
            # Create events for next 2 weekends
            for week_offset in range(2):
                for day_offset in [5, 6]:  # Saturday and Sunday
                    event_date = now + timedelta(days=(day_offset - now.weekday() + week_offset * 7))
                    
                    if event_date < now:
                        continue
                    
                    event_datetime = event_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    
                    try:
                        event = Event(
                            title=f"{trail['name']} - Family Hiking",
                            description=f"{trail['description']} Distance: {trail['distance']}. Difficulty: {trail['difficulty']}. Great for families to enjoy Colorado's beautiful outdoor spaces together. Remember to bring water and wear appropriate footwear.",
                            date_start=event_datetime,
                            date_end=event_datetime + timedelta(hours=3),
                            location_name=location['name'],
                            address=f"{location['name']}, {location['city']}, CO",
                            city=location['city'],
                            latitude=location['coordinates'][0],
                            longitude=location['coordinates'][1],
                            age_group=self._get_age_group_from_difficulty(trail['difficulty']),
                            categories=["outdoor", "hiking", "nature", "family", "exercise"],
                            price_type=PriceType.FREE,
                            source_url=trail.get('real_url', f"https://www.alltrails.com/trail/{trail['name'].lower().replace(' ', '-').replace("'", '')}"),
                            image_url=f"https://picsum.photos/400/300?random=curated{hash(trail['name']) % 1000}"
                        )
                        
                        events.append(event)
                        
                    except Exception as e:
                        logger.error(f"Error creating curated trail event: {e}")
                        continue
            
            # Limit to 1-2 events per trail to avoid too many
            if len(events) >= 10:
                break
        
        logger.info(f"🥾 Created {len(events)} curated hiking trail events")
        return events

if __name__ == "__main__":
    scraper = AllTrailsScraper()
    events = scraper.scrape_events()
    
    print(f"🥾 Found {len(events)} hiking trail events:")
    for event in events[:5]:  # Show first 5
        print(f"🏔️ {event.title}")
        print(f"   📍 {event.location_name}, {event.city}")
        print(f"   📅 {event.date_start.strftime('%A, %B %d at %I:%M %p')}")
        print(f"   👥 {event.age_group.value}")
        print(f"   🥾 {', '.join(event.categories)}")
        print(f"   💰 {event.price_type.value}")
        print() 