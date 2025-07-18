# PRD – The Outworld Scraper & API

## Objective
Build an automated backend that extracts, stores, and exposes family event data in Colorado for children (0–10 years) to feed The Outworld app.

## Features

### 1. Scraper
- Scrapes events from public sites (Macaroni KID, Visit Denver, libraries, parks, etc.)
- Classifies by:
  - Age: babies (0-1), toddlers (2–3), kids (4–6), youth (7–10)
  - Category: science, nature, reading, food, music, art, animals, etc.
- Runs scraping every 24h automatically (cron or APScheduler)
- Avoids duplicates
- Supports individual scrapers per source

### 2. Database
- PostgreSQL
- Main model: `Event`
  - id, title, description, date_start, date_end, location_name, address, city, lat/lng, age_group, categories[], price_type, source_url, image_url, last_updated

### 3. API (FastAPI)
- GET `/events`: all events
- GET `/events/today`
- GET `/events?city=denver&age_group=kids&category=science`
- Endpoint to check scraping status or logs

## MVP
- 3 initial scrapers: Macaroni KID (Denver), Visit Boulder, Boulder Parks & Open Space
- 1 daily job that runs scrapers and updates the database
- Basic API working and ready to be connected to frontend

## Tech Stack
- Python + FastAPI + SQLAlchemy
- PostgreSQL
- Scraping with BeautifulSoup and/or Playwright
- Hosting: Railway, Render or Supabase (DB)
- Later: Firebase Auth or Supabase Auth for parent login

## Flow
1. Scrapers → insert/update in PostgreSQL
2. FastAPI exposes the data
3. App (React Native) consumes the API 