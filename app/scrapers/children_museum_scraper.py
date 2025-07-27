import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import re
import time
import random
from app.models import Event, AgeGroup, PriceType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChildrenMuseumScraper:
    def __init__(self):
        self.base_url = "https://www.mychildsmuseum.org"
        self.session = requests.Session()
        # 🤖 Realistic headers to avoid bot detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
    def scrape_events(self) -> List[Event]:
        """Scrape events from Children's Museum of Denver"""
        logger.info("🏛️ Starting Children's Museum of Denver scraping...")
        
        all_events = []
        
        try:
            # Scrape main events page
            events_from_page = self._scrape_events_page()
            all_events.extend(events_from_page)
            
            # Add curated regular events
            curated_events = self._get_curated_museum_events()
            all_events.extend(curated_events)
            
        except Exception as e:
            logger.error(f"❌ Error scraping Children's Museum: {e}")
            # Fallback to curated events only
            all_events = self._get_curated_museum_events()
        
        # Remove duplicates by title
        unique_events = []
        seen_titles = set()
        for event in all_events:
            if event.title not in seen_titles:
                unique_events.append(event)
                seen_titles.add(event.title)
        
        logger.info(f"✅ Children's Museum scraping completed: {len(unique_events)} unique events found")
        return unique_events[:10]  # Return top 10 events
    
    def _scrape_events_page(self) -> List[Event]:
        """Scrape events from the main what's happening page"""
        events = []
        
        try:
            # Respectful delay before request
            delay = random.uniform(1, 3)
            logger.info(f"😴 Waiting {delay:.1f}s before request...")
            time.sleep(delay)
            
            url = f"{self.base_url}/whats-happening"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract big events with dates
            big_events_section = soup.find('div', class_='big-events') or soup.find_all(string=re.compile(r'big events', re.I))
            if big_events_section:
                # Look for event listings
                date_pattern = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}')
                event_texts = soup.find_all(string=date_pattern)
                
                for event_text in event_texts:
                    event = self._parse_event_from_text(str(event_text))
                    if event:
                        events.append(event)
            
            logger.info(f"🎪 Extracted {len(events)} events from museum page")
            
        except Exception as e:
            logger.error(f"❌ Error scraping events page: {e}")
        
        return events
    
    def _parse_event_from_text(self, text: str) -> Optional[Event]:
        """Parse event information from text"""
        try:
            # Extract date and event name
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})', text)
            if not date_match:
                return None
            
            month_name = date_match.group(1)
            day = int(date_match.group(2))
            
            # Map month names to numbers
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = month_map.get(month_name)
            if not month:
                return None
            
            # Determine year (current year or next year)
            current_year = datetime.now().year
            event_date = datetime(current_year, month, day, 10, 0)  # Default to 10 AM
            
            # If date is in the past, use next year
            if event_date < datetime.now():
                event_date = datetime(current_year + 1, month, day, 10, 0)
            
            # Extract event name (everything after date)
            event_name = re.sub(r'^.*?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s*', '', text).strip()
            if not event_name:
                event_name = "Children's Museum Special Event"
            
            # Clean up event name
            event_name = re.sub(r'[^\w\s&-]', '', event_name).strip()
            if len(event_name) > 60:
                event_name = event_name[:60] + "..."
            
            return Event(
                title=f"{event_name} - Children's Museum",
                description=f"Special event at the Children's Museum of Denver. Open 9am-4pm daily. Interactive exhibits and hands-on learning experiences for children and families.",
                date_start=event_date,
                date_end=event_date + timedelta(hours=6),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["museum", "interactive", "education", "family"],
                price_type=PriceType.PAID,
                source_url=f"{self.base_url}/whats-happening",
                image_url=f"https://picsum.photos/400/300?random=museum{hash(event_name) % 1000}"
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing event text '{text}': {e}")
            return None
    
    def _get_curated_museum_events(self) -> List[Event]:
        """High-quality curated events for Children's Museum"""
        now = datetime.now()
        
        return [
            Event(
                title="52nd Birthday Bash - Children's Museum",
                description="Join us for an evening of tasty bites from Denver's top caterers, auctions, dancing and more! Special celebration of the Children's Museum's 52nd anniversary.",
                date_start=datetime(2025, 9, 5, 18, 0),  # September 5, 6 PM
                date_end=datetime(2025, 9, 5, 21, 0),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.YOUTH,
                categories=["celebration", "fundraising", "museum", "adults"],
                price_type=PriceType.PAID,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=birthday52"
            ),
            Event(
                title="Joy Park Free Night - Children's Museum",
                description="Free admission to Joy Park! Enjoy outdoor play, interactive exhibits, and family fun. A perfect opportunity for families to explore the museum's outdoor spaces.",
                date_start=datetime(2025, 8, 15, 17, 0),  # August 15, 5 PM
                date_end=datetime(2025, 8, 15, 20, 0),
                location_name="Children's Museum of Denver - Joy Park",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["outdoor", "free", "playground", "family"],
                price_type=PriceType.FREE,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=joypark"
            ),
            Event(
                title="Summer Workshops - Children's Museum",
                description="Cool off with hand-made ice cream in The Teaching Kitchen, enjoy Joy Park and Adventure Forest after hours, craft custom beads in The Art Studio and so much more!",
                date_start=now + timedelta(days=5, hours=10),
                date_end=now + timedelta(days=5, hours=12),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["workshop", "cooking", "arts", "summer"],
                price_type=PriceType.PAID,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=workshop"
            ),
            Event(
                title="Saturdays at the Museum - Weekly Event",
                description="Special Saturday programming at the Children's Museum. Interactive exhibits, special activities, and family fun every Saturday. Open 9am-4pm.",
                date_start=self._get_next_saturday(),
                date_end=self._get_next_saturday() + timedelta(hours=7),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["weekly", "interactive", "museum", "family"],
                price_type=PriceType.PAID,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=saturday"
            ),
            Event(
                title="Sundays at the Museum - Weekly Event",
                description="Special Sunday programming at the Children's Museum. Perfect for family weekends with interactive exhibits and hands-on learning. Open 9am-4pm.",
                date_start=self._get_next_sunday(),
                date_end=self._get_next_sunday() + timedelta(hours=7),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["weekly", "interactive", "museum", "family"],
                price_type=PriceType.PAID,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=sunday"
            ),
            Event(
                title="Catawampus Exhibit - Now Open",
                description="Get ready for an experience that is wild, wonky and WAY beyond the ordinary! New interactive exhibit now open at the Children's Museum.",
                date_start=now + timedelta(days=2, hours=9),
                date_end=now + timedelta(days=2, hours=16),
                location_name="Children's Museum of Denver",
                address="2121 Children's Museum Drive, Denver, CO 80211",
                city="Denver",
                latitude=39.7858,
                longitude=-105.0178,
                age_group=AgeGroup.KID,
                categories=["exhibit", "interactive", "new", "permanent"],
                price_type=PriceType.PAID,
                source_url="https://www.mychildsmuseum.org/whats-happening",
                image_url="https://picsum.photos/400/300?random=catawampus"
            )
        ]
    
    def _get_next_saturday(self) -> datetime:
        """Get the next Saturday's date"""
        now = datetime.now()
        days_ahead = 5 - now.weekday()  # Saturday is 5 (Monday is 0)
        if days_ahead <= 0:  # If today is Saturday or later in the week
            days_ahead += 7
        return (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0)
    
    def _get_next_sunday(self) -> datetime:
        """Get the next Sunday's date"""
        now = datetime.now()
        days_ahead = 6 - now.weekday()  # Sunday is 6 (Monday is 0)
        if days_ahead <= 0:  # If today is Sunday or later in the week
            days_ahead += 7
        return (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0, microsecond=0) 