# The Outworld Scraper API

A FastAPI backend that scrapes, stores, and exposes family event data in Colorado for children (0–10 years).

## Project Structure

```
the-outworld-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # Supabase connection handler
│   ├── models.py            # Pydantic models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── events.py        # Event routes
│   └── scrapers/
│       ├── __init__.py
│       └── macaronikid.py   # Mock scraper
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Supabase Database

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings → API to find your URL and anon key
3. In the SQL editor, create the events table:

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    date_start TIMESTAMP WITH TIME ZONE NOT NULL,
    date_end TIMESTAMP WITH TIME ZONE NOT NULL,
    location_name VARCHAR NOT NULL,
    address VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    age_group VARCHAR NOT NULL CHECK (age_group IN ('baby', 'toddler', 'kid', 'youth')),
    categories TEXT[] NOT NULL,
    price_type VARCHAR NOT NULL CHECK (price_type IN ('free', 'paid')),
    source_url VARCHAR NOT NULL,
    image_url VARCHAR,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual Supabase credentials
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key-here
```

### 4. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Or run directly
python app/main.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Events

- `GET /api/v1/events` - Get all events
- `GET /api/v1/events/today` - Get today's events
- `GET /api/v1/events/status` - Get scraping status

### Filtering

You can filter events using query parameters:

```bash
# Filter by city
GET /api/v1/events?city=Denver

# Filter by age group
GET /api/v1/events?age_group=kid

# Filter by category
GET /api/v1/events?category=science

# Multiple filters
GET /api/v1/events?city=Denver&age_group=kid&category=science
```

### Other Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check

## Development

The mock scraper in `app/scrapers/macaronikid.py` generates 3 sample events at startup. To add real scrapers:

1. Create new scraper files in `app/scrapers/`
2. Follow the same pattern as `macaronikid.py`
3. Import and call from `app/main.py`

## Tech Stack

- **FastAPI** - Web framework
- **Supabase** - PostgreSQL database
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variables
- **Uvicorn** - ASGI server 