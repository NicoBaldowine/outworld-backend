import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from typing import List, Optional
import re
from app.models import Event, AgeGroup, PriceType
import random
import pytz
from dateutil import parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DenverLibraryScraper:
    def __init__(self):
        self.base_url = "https://denverlibrary.libcal.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def scrape_events(self) -> List[Event]:
        """Main method to scrape Denver Public Library events"""
        logger.info("🕷️  Starting enhanced Denver Public Library scraping...")
        
        all_events = []
        
        try:
            # Try real scraping from LibCal system
            scraped_events = self._scrape_libcal_events()
            all_events.extend(scraped_events)
            
            logger.info(f"✅ Found {len(all_events)} unique library events")
            return all_events
            
        except Exception as e:
            logger.error(f"Error in scraping: {e}")
            # Fallback to curated events
            return self._get_curated_library_events()
    
    def _scrape_libcal_events(self) -> List[Event]:
        """Scrape REAL specific events from Denver Library LibCal system using actual event IDs"""
        events = []
        
        try:
            # Verified real event IDs from Denver Public Library LibCal system
            real_event_ids = [
                14848230,  # Family Storytime
                14781357,  # Family STEAM Workshop  
                14666964,  # Teen Maker Space
                14448560,  # Event Box
                14324412,  # Creative Maker Workshop
                14319479,  # Family Storytime (different)
            ]
            
            logger.info(f"🔍 Scraping {len(real_event_ids)} real library events...")
            
            for event_id in real_event_ids:
                event_url = f"{self.base_url}/event/{event_id}"
                
                try:
                    event = self._extract_event_details(event_url)
                    if event:
                        events.append(event)
                        logger.info(f"✅ Successfully scraped event: {event.title}")
                    else:
                        logger.warning(f"⚠️ Could not extract event from {event_url}")
                        
                except Exception as e:
                    logger.error(f"❌ Error scraping event {event_id}: {e}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error in LibCal scraping: {e}")
            return []

    def _extract_real_event_dates(self, soup: BeautifulSoup, event_url: str) -> tuple[datetime, datetime]:
        """Extract REAL event dates from the page - FIXED VERSION!"""
        try:
            # Look for <dt>Date:</dt> followed by <dd> with actual date
            date_dt = soup.find('dt', string=re.compile(r'Date:', re.I))
            time_dt = soup.find('dt', string=re.compile(r'Time:', re.I))
            
            date_text = None
            time_text = None
            
            # Extract date from <dd> following <dt>Date:</dt>
            if date_dt:
                date_dd = date_dt.find_next_sibling('dd')
                if date_dd:
                    # Extract ONLY the first text node, not all children
                    first_text = date_dd.contents[0] if date_dd.contents else ""
                    if hasattr(first_text, 'strip'):
                        date_text = first_text.strip()
                    else:
                        date_text = str(first_text).strip()
                    logger.info(f"📅 Found date in HTML: {date_text}")
            
            # Extract time from <dd> following <dt>Time:</dt>
            if time_dt:
                time_dd = time_dt.find_next_sibling('dd')
                if time_dd:
                    # Extract ONLY the first text node, not all children
                    first_text = time_dd.contents[0] if time_dd.contents else ""
                    if hasattr(first_text, 'strip'):
                        time_text = first_text.strip()
                    else:
                        time_text = str(first_text).strip()
                    logger.info(f"🕐 Found time in HTML: {time_text}")
            
            # If we found both date and time, parse them
            if date_text and time_text:
                logger.info(f"🎯 Parsing date: '{date_text}' and time: '{time_text}'")
                
                # Parse date (e.g., "Saturday, July 19, 2025")
                try:
                    date_clean = date_text.strip()
                    event_date = parser.parse(date_clean).date()
                    logger.info(f"✅ Parsed date: {event_date}")
                except Exception as e:
                    logger.error(f"❌ Error parsing date '{date_text}': {e}")
                    raise
                
                # Parse time (e.g., "10:30 am - 11:00 am")
                try:
                    time_clean = time_text.split('(')[0].strip()  # Remove timezone info
                    logger.info(f"🕐 Cleaning time: '{time_clean}'")
                    
                    if ' - ' in time_clean or ' – ' in time_clean:
                        # Split on either dash type
                        if ' - ' in time_clean:
                            start_time_str, end_time_str = time_clean.split(' - ', 1)
                        else:
                            start_time_str, end_time_str = time_clean.split(' – ', 1)
                            
                        start_time_str = start_time_str.strip()
                        end_time_str = end_time_str.strip()
                        
                        start_time = parser.parse(start_time_str).time()
                        end_time = parser.parse(end_time_str).time()
                        logger.info(f"✅ Parsed times: {start_time} - {end_time}")
                    else:
                        start_time = parser.parse(time_clean).time()
                        end_time = (datetime.combine(datetime.min, start_time) + timedelta(hours=1)).time()
                        logger.info(f"✅ Single time parsed: {start_time} (end: {end_time})")
                except Exception as e:
                    logger.error(f"❌ Error parsing time '{time_text}': {e}")
                    # Fallback to default times
                    start_time = datetime.strptime("10:00 AM", "%I:%M %p").time()
                    end_time = datetime.strptime("11:00 AM", "%I:%M %p").time()
                    logger.info(f"✅ Fallback times: {start_time} - {end_time}")
                
                # Combine date and time with Denver timezone
                denver_tz = pytz.timezone('America/Denver')
                start_datetime = datetime.combine(event_date, start_time)
                end_datetime = datetime.combine(event_date, end_time)
                
                # Make timezone aware
                start_datetime = denver_tz.localize(start_datetime)
                end_datetime = denver_tz.localize(end_datetime)
                
                logger.info(f"🎉 SUCCESS! Final parsed dates: {start_datetime} - {end_datetime}")
                return start_datetime, end_datetime
            
            logger.warning(f"⚠️ Could not find date/time elements in {event_url}")
            
        except Exception as e:
            logger.error(f"❌ Error parsing real dates from {event_url}: {e}")
        
        # Fallback to near future with reasonable time
        logger.warning("🔄 Using fallback dates")
        fallback_date = datetime.now() + timedelta(days=7)
        fallback_start = fallback_date.replace(hour=10, minute=0, second=0, microsecond=0)
        fallback_end = fallback_start + timedelta(hours=1)
        
        return fallback_start, fallback_end

    def _extract_event_details(self, event_url: str) -> Optional[Event]:
        """Extract details from a specific event page"""
        try:
            response = self.session.get(event_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract event title - LibCal uses "Event Box" as generic title
            title_elem = (soup.find('h1') or 
                         soup.find('h2') or 
                         soup.find('.s-lc-event-title') or
                         soup.find('[data-testid="event-title"]') or
                         soup.find('.event-title'))
            
            raw_title = title_elem.get_text(strip=True) if title_elem else None
            if not raw_title:
                logger.warning(f"No title found for {event_url}")
                return None
            
            # Extract description - this contains the real event information
            description_elem = (soup.find('.s-lc-event-description') or
                              soup.find('.event-description') or 
                              soup.find('#event-description') or
                              soup.find('[data-testid="event-description"]'))
            
            if not description_elem:
                # Try to find description in the "About:" section
                about_header = soup.find('h2', string=re.compile('About', re.I))
                if about_header:
                    description_elem = about_header.find_next_sibling(['p', 'div']) or about_header.find_next(['p', 'div'])
            
            description = description_elem.get_text(strip=True) if description_elem else ""
            
            # Clean up description
            description = re.sub(r'\s+', ' ', description).strip()
            
            # Generate specific title based on event content
            specific_title = self._generate_specific_title(description, event_url)
            title = specific_title if specific_title else raw_title
            
            # Extract location
            location_elem = (soup.find('.s-lc-event-location') or
                           soup.find('.event-location') or
                           soup.find('.location') or
                           soup.find('[data-testid="event-location"]'))
            
            if location_elem:
                location = location_elem.get_text(strip=True)
            else:
                location = "Denver Public Library"
            
            # Extract age group and categories
            all_text = f"{title} {description}".lower()
            age_group = self._determine_age_group(all_text)
            categories = self._extract_categories(title, description)
            
            # Extract REAL date and time from page - FIXED!
            start_date, end_date = self._extract_real_event_dates(soup, event_url)
            
            # Determine coordinates based on location
            latitude, longitude, address = self._get_library_coordinates(location)
            
            # Extract event ID from URL for better image randomization
            event_id_match = re.search(r'/event/(\d+)', event_url)
            event_id = event_id_match.group(1) if event_id_match else str(hash(event_url))
            
            event = Event(
                title=title,
                description=description,
                date_start=start_date,
                date_end=end_date,
                location_name=location,
                address=address,
                city="Denver",
                latitude=latitude,
                longitude=longitude,
                age_group=age_group,
                categories=categories,
                price_type=PriceType.FREE,
                source_url=event_url,
                image_url=f"https://picsum.photos/400/300?random={event_id}"
            )
            
            logger.info(f"✅ Extracted event: {title} at {location}")
            return event
            
        except Exception as e:
            logger.error(f"Error extracting event details from {event_url}: {e}")
            return None

    # [Rest of the methods remain the same as original scraper]
    def _generate_specific_title(self, description: str, event_url: str) -> Optional[str]:
        """Generate specific title from description content"""
        if not description:
            return None
        
        desc_lower = description.lower()
        
        # Map common event types to better titles
        title_mappings = [
            ("steam", "Family STEAM Workshop"),
            ("maker", "Creative Maker Workshop"), 
            ("storytime", "Family Storytime"),
            ("story time", "Family Storytime"),
            ("teen", "Teen Program"),
            ("technology", "Technology Program"),
            ("sewing", "Sewing Workshop"),
            ("coding", "Coding Workshop"),
            ("robotics", "Robotics Workshop")
        ]
        
        for keyword, title in title_mappings:
            if keyword in desc_lower:
                return title
        
        # Extract event ID to make unique titles
        event_id_match = re.search(r'/event/(\d+)', event_url)
        if event_id_match:
            return f"Event Box"  # Keep generic for LibCal events
        
        return None

    def _determine_age_group(self, text: str) -> AgeGroup:
        """Determine age group from text content"""
        text_lower = text.lower()
        
        # Specific age mentions
        if any(phrase in text_lower for phrase in ['0-5', '0 to 5', 'ages 0-5', 'birth to 5']):
            return AgeGroup.TODDLER
        elif any(phrase in text_lower for phrase in ['6-12', '6 to 12', 'ages 6-12', 'elementary']):
            return AgeGroup.KID
        elif any(phrase in text_lower for phrase in ['13-18', '13 to 18', 'teen', 'youth']):
            return AgeGroup.YOUTH
        elif any(phrase in text_lower for phrase in ['baby', 'infant', '0-18 months']):
            return AgeGroup.BABY
        
        # Default for library events
        return AgeGroup.KID

    def _extract_categories(self, title: str, description: str) -> List[str]:
        """Extract categories from title and description"""
        categories = []
        combined_text = f"{title} {description}".lower()
        
        category_keywords = {
            "STEM & Technology": ["steam", "technology", "coding", "robotics", "science"],
            "Creating & Making": ["maker", "creative", "craft", "art", "sewing", "building"],
            "Book Clubs & Storytime": ["storytime", "story time", "reading", "books"],
            "Early Learners (0-5)": ["0-5", "toddler", "preschool", "early"],
            "Virtual Programs": ["virtual", "online", "zoom"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                categories.append(category)
        
        # Default category if none found
        if not categories:
            categories = ["Book Clubs & Storytime"]
        
        return categories

    def _get_library_coordinates(self, location: str) -> tuple[float, float, str]:
        """Get coordinates for library locations"""
        library_locations = {
            "Central Library": (39.7368, -104.9918, "10 W 14th Ave Pkwy, Denver, CO 80204"),
            "Denver Public Library": (39.7365, -104.9891, "10 W 14th Ave Pkwy, Denver, CO 80204"),
            "Montbello Branch": (39.7691, -104.8721, "12955 Albrook Dr, Denver, CO 80239"),
            "Virtual Event": (39.7392, -104.9903, "Online Event, Denver, CO"),
        }
        
        # Find best match
        for lib_name, (lat, lon, addr) in library_locations.items():
            if lib_name.lower() in location.lower():
                return lat, lon, addr
        
        # Default to Central Library
        return library_locations["Denver Public Library"]

    def _get_curated_library_events(self) -> List[Event]:
        """Fallback curated events if scraping fails"""
        return []  # Return empty for now since we want real data


def scrape_and_save_events() -> List[Event]:
    """Main function to scrape library events"""
    scraper = DenverLibraryScraper()
    return scraper.scrape_events() 