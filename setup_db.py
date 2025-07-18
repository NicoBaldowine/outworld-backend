#!/usr/bin/env python3
"""
Script to set up the database table in Supabase
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_events_table():
    """Create the events table in Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(url, key)
        
        # SQL to create the events table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
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
            last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        
        print("✅ Events table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        print("💡 Please create the table manually in Supabase SQL editor:")
        print(create_table_sql)
        return False

if __name__ == "__main__":
    print("🚀 Setting up database table...")
    create_events_table() 