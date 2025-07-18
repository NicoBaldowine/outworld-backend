import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
import pytz
from app.database import DatabaseHandler
from app.models import Event

# Import all scrapers - using improved versions
# from app.scrapers.macaronikid_scraper import MacaroniKidDenverScraper
# from app.scrapers.colorado_parent_scraper import ColoradoParentScraper
from app.scrapers.denver_events_scraper import DenverEventsScraper
# from app.scrapers.denver_recreation_scraper import DenverRecreationScraper
from app.scrapers.denver_library_scraper import DenverLibraryScraper
from app.scrapers.kids_out_about_scraper import KidsOutAboutScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Statistics tracking
class ScrapingStats:
    def __init__(self):
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.total_events_scraped = 0
        self.last_run_time = None
        self.last_success_time = None
        self.last_error = None
        self.events_by_source = {}
        self.events_by_age_group = {}
        self.events_by_category = {}
        self.events_without_images = 0  # Track events without images
    
    def update_run_stats(self, success: bool, events_count: int, error: str = None):
        """Update run statistics"""
        self.total_runs += 1
        self.last_run_time = datetime.now()
        
        if success:
            self.successful_runs += 1
            self.total_events_scraped += events_count
            self.last_success_time = datetime.now()
        else:
            self.failed_runs += 1
            if error:
                self.last_error = error
    
    def update_event_stats(self, events: List[Event]):
        """Update event statistics"""
        for event in events:
            # Track by source
            source = event.source_url.split('/')[2] if event.source_url else 'unknown'
            self.events_by_source[source] = self.events_by_source.get(source, 0) + 1
            
            # Track by age group
            age_group = event.age_group.value
            self.events_by_age_group[age_group] = self.events_by_age_group.get(age_group, 0) + 1
            
            # Track by categories
            for category in event.categories:
                self.events_by_category[category] = self.events_by_category.get(category, 0) + 1
            
            # Track events without images
            if not event.image_url:
                self.events_without_images += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics dictionary"""
        return {
            'total_runs': self.total_runs,
            'successful_runs': self.successful_runs,
            'failed_runs': self.failed_runs,
            'total_events_scraped': self.total_events_scraped,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'last_error': self.last_error,
            'events_by_source': self.events_by_source,
            'events_by_age_group': self.events_by_age_group,
            'events_by_category': self.events_by_category,
            'events_without_images': self.events_without_images,
            'success_rate': (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0
        }

# Global statistics instance
stats = ScrapingStats()

class EventScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = DatabaseHandler()
        self.denver_timezone = pytz.timezone('America/Denver')
        
        # ONLY 3 scrapers that user wants - using improved versions
        self.scrapers = {
            'denver_library': DenverLibraryScraper(),
            'kids_out_about': KidsOutAboutScraper(),
            'denver_events': DenverEventsScraper()
        }
        
        logger.info("🗓️  Event scheduler initialized with 3 specific scrapers: denver_library, kids_out_about, denver_events")
    
    def ensure_image_url(self, event: Event) -> bool:
        """Ensure event has an image URL - required for all events"""
        if not event.image_url:
            logger.error(f"❌ Event '{event.title}' missing required image_url")
            return False
        return True
    
    def validate_event(self, event: Event) -> bool:
        """Validate event data - ensure all required fields including image"""
        if not self.ensure_image_url(event):
            return False
        
        # Check other required fields
        if not event.title or not event.description:
            logger.error(f"❌ Event missing title or description")
            return False
        
        if not event.location_name or not event.address:
            logger.error(f"❌ Event missing location information")
            return False
        
        return True
    
    async def scrape_all_sources(self) -> List[Event]:
        """Scrape events from all available sources"""
        all_events = []
        
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"🕷️  Scraping {source_name}...")
                
                # All scrapers are now class-based with improved functionality
                events = scraper.scrape_events()
                
                # Validate all events have images
                valid_events = []
                for event in events:
                    if self.validate_event(event):
                        valid_events.append(event)
                    else:
                        logger.warning(f"⚠️  Skipping invalid event: {event.title}")
                
                all_events.extend(valid_events)
                logger.info(f"✅ Successfully scraped {len(valid_events)} valid events from {source_name}")
                
            except Exception as e:
                logger.error(f"❌ Error scraping {source_name}: {e}")
                continue
        
        logger.info(f"📊 Total events scraped from all sources: {len(all_events)}")
        return all_events
    
    async def run_scheduled_scraping(self):
        """Run the scheduled scraping process"""
        logger.info("🚀 Starting scheduled scraping process...")
        
        try:
            # Scrape events from all sources
            events = await self.scrape_all_sources()
            
            if not events:
                logger.warning("⚠️  No events found from any source")
                stats.update_run_stats(False, 0, "No events found from any source")
                return
            
            # Save events to database
            new_events = []
            for event in events:
                if not self.db.event_exists(event.title, event.date_start, event.location_name):
                    new_events.append(event)
            
            if new_events:
                self.db.save_events(new_events)
                logger.info(f"💾 Saved {len(new_events)} new events to database")
            else:
                logger.info("ℹ️  No new events to save (all events already exist)")
            
            # Update statistics
            stats.update_run_stats(True, len(events))
            stats.update_event_stats(events)
            
            logger.info("✅ Scheduled scraping completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in scheduled scraping: {e}")
            stats.update_run_stats(False, 0, str(e))
    
    async def run_weekly_cleanup(self):
        """Run weekly cleanup to remove old events"""
        logger.info("🧹 Starting weekly cleanup process...")
        
        try:
            # Remove events older than 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = self.db.delete_old_events(cutoff_date)
            
            logger.info(f"🗑️  Deleted {deleted_count} old events from database")
            
        except Exception as e:
            logger.error(f"❌ Error in weekly cleanup: {e}")
    
    async def run_daily_cleanup(self):
        """Run daily cleanup to remove expired events"""
        logger.info("🧹 Starting daily cleanup process...")
        
        try:
            # Remove events that have already ended (expired)
            cutoff_datetime = datetime.now()
            deleted_count = self.db.delete_expired_events(cutoff_datetime)
            
            logger.info(f"🗑️  Deleted {deleted_count} expired events from database")
            
        except Exception as e:
            logger.error(f"❌ Error in daily cleanup: {e}")
    
    async def start(self):
        """Start the scheduler"""
        try:
            # Schedule daily scraping at 6 AM Denver time
            self.scheduler.add_job(
                self.run_scheduled_scraping,
                CronTrigger(hour=6, minute=0, timezone=self.denver_timezone),
                id='daily_scraping',
                name='Daily Event Scraping',
                replace_existing=True
            )
            
            # Schedule daily cleanup at 1 AM Denver time (before scraping)
            self.scheduler.add_job(
                self.run_daily_cleanup,
                CronTrigger(hour=1, minute=0, timezone=self.denver_timezone),
                id='daily_cleanup',
                name='Daily Event Cleanup',
                replace_existing=True
            )
            
            # Schedule weekly cleanup on Sundays at 2 AM Denver time (for deep cleaning)
            self.scheduler.add_job(
                self.run_weekly_cleanup,
                CronTrigger(day_of_week=6, hour=2, minute=0, timezone=self.denver_timezone),
                id='weekly_cleanup',
                name='Weekly Database Cleanup',
                replace_existing=True
            )
            
            logger.info("✅ Scheduler started successfully")
            logger.info("🗓️  Daily scraping scheduled for 6:00 AM Denver time")
            logger.info("🧹 Daily cleanup scheduled for 1:00 AM Denver time")
            logger.info("🧹 Weekly cleanup scheduled for Sundays at 2:00 AM Denver time")
            
            # Start the scheduler
            self.scheduler.start()
            
            # Log next run times
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                logger.info(f"⏰ Next run for '{job.name}': {job.next_run_time}")
            
        except Exception as e:
            logger.error(f"❌ Error starting scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("🛑 Event scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    async def run_manual_scraping(self) -> Dict[str, Any]:
        """Run manual scraping and return results"""
        logger.info("🔧 Running manual scraping...")
        
        try:
            # Run the scraping process
            await self.run_scheduled_scraping()
            
            # Return results
            return {
                'success': True,
                'message': 'Manual scraping completed successfully',
                'timestamp': datetime.now().isoformat(),
                'statistics': stats.get_stats()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in manual scraping: {e}")
            return {
                'success': False,
                'message': f'Manual scraping failed: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        jobs = self.scheduler.get_jobs()
        job_info = []
        
        for job in jobs:
            job_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'running': self.scheduler.running,
            'jobs': job_info,
            'statistics': stats.get_stats(),
            'scrapers_available': list(self.scrapers.keys())
        }
    
    def get_next_run_time(self) -> Dict[str, Any]:
        """Get next scheduled run time"""
        daily_job = self.scheduler.get_job('daily_scraping')
        daily_cleanup_job = self.scheduler.get_job('daily_cleanup')
        cleanup_job = self.scheduler.get_job('weekly_cleanup')
        
        return {
            'daily_scraping': daily_job.next_run_time.isoformat() if daily_job and daily_job.next_run_time else None,
            'daily_cleanup': daily_cleanup_job.next_run_time.isoformat() if daily_cleanup_job and daily_cleanup_job.next_run_time else None,
            'weekly_cleanup': cleanup_job.next_run_time.isoformat() if cleanup_job and cleanup_job.next_run_time else None
        }

# Global scheduler instance
scheduler = EventScheduler()

# Functions for external use
async def start_scheduler():
    """Start the event scheduler"""
    await scheduler.start()

async def stop_scheduler():
    """Stop the event scheduler"""
    await scheduler.stop()

async def run_manual_scraping():
    """Run manual scraping"""
    return await scheduler.run_manual_scraping()

def get_scheduler_status():
    """Get scheduler status"""
    return scheduler.get_scheduler_status()

def get_next_run_time():
    """Get next run time"""
    return scheduler.get_next_run_time()

def get_scraping_stats():
    """Get scraping statistics"""
    return stats.get_stats() 