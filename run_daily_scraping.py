#!/usr/bin/env python3
"""
Daily scraping script for The Outworld Scraper
This script runs all 6 scrapers and updates the database
Can be used with cron jobs for automatic scheduling
"""

import asyncio
import logging
import sys
from datetime import datetime
import pytz
from app.scheduler import run_manual_scraping
from app.database import database_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Run daily scraping of all 6 scrapers"""
    denver_tz = pytz.timezone('America/Denver')
    now = datetime.now(denver_tz)
    
    logger.info("🚀 STARTING DAILY SCRAPING")
    logger.info("=" * 50)
    logger.info(f"📅 Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    logger.info("📊 Scrapers: Library, Kids Out, Movies, Hiking, Children Museum, Zoo")
    
    try:
        # Get initial event count
        initial_events = database_handler.get_all_events()
        initial_count = len(initial_events)
        logger.info(f"📋 Initial events in database: {initial_count}")
        
        # Run scraping
        logger.info("🕷️ Starting scraping process...")
        result = await run_manual_scraping()
        
        # Get final event count
        final_events = database_handler.get_all_events()
        final_count = len(final_events)
        new_events = final_count - initial_count
        
        logger.info("✅ DAILY SCRAPING COMPLETED")
        logger.info(f"📊 Results:")
        logger.info(f"   • Initial events: {initial_count}")
        logger.info(f"   • Final events: {final_count}")
        logger.info(f"   • New events added: {new_events}")
        logger.info(f"   • Success: {result.get('success', False)}")
        
        if new_events > 0:
            logger.info(f"🎉 Successfully added {new_events} new events!")
        else:
            logger.info("ℹ️ No new events found (database up to date)")
            
    except Exception as e:
        logger.error(f"❌ Error during daily scraping: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 