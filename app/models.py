from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgeGroup(str, Enum):
    BABY = "baby"
    TODDLER = "toddler"
    KID = "kid"
    YOUTH = "youth"


class PriceType(str, Enum):
    FREE = "free"
    PAID = "paid"


class Event(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    date_start: datetime
    date_end: datetime
    location_name: str
    address: str
    city: str
    latitude: float
    longitude: float
    age_group: AgeGroup
    categories: List[str]
    price_type: PriceType
    source_url: str
    image_url: Optional[str] = None
    last_updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    date_start: datetime
    date_end: datetime
    location_name: str
    address: str
    city: str
    latitude: float
    longitude: float
    age_group: str
    categories: List[str]
    price_type: str
    source_url: str
    image_url: Optional[str]
    last_updated_at: datetime 