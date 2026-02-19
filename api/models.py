"""
Modèles Pydantic pour l'API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class CategoryBase(BaseModel):
    """Catégorie de base"""
    id: int
    name: str
    parent_category: Optional[str] = None


class CityBase(BaseModel):
    """Ville de base"""
    id: int
    name: str
    event_count: Optional[int] = 0


class EventBase(BaseModel):
    """Événement minimal"""
    id: int
    title: str
    event_date: Optional[date] = None
    arrondissement: Optional[str] = None
    is_free: bool = False
    
    class Config:
        from_attributes = True


class EventDetail(EventBase):
    """Événement détaillé"""
    description: Optional[str] = None
    
    # Localisation
    city_name: Optional[str] = None
    address_street: Optional[str] = None
    address_name: Optional[str] = None
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_center: Optional[float] = None
    
    # Dates
    event_datetime: Optional[datetime] = None
    year: Optional[int] = None
    month: Optional[int] = None
    month_name: Optional[str] = None
    day_of_week_name: Optional[str] = None
    season: Optional[str] = None
    time_period: Optional[str] = None
    is_weekend: bool = False
    is_multi_day: bool = False
    duration_days: Optional[int] = None
    
    # Prix
    price_type: Optional[str] = None
    price_detail: Optional[str] = None
    accessibility_score: Optional[float] = None
    
    # Contact
    contact_url: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Catégorie
    category_name: Optional[str] = None
    parent_category: Optional[str] = None
    
    class Config:
        from_attributes = True


class EventList(BaseModel):
    """Liste paginée d'événements"""
    total: int
    page: int
    page_size: int
    total_pages: int
    events: List[EventBase]


class Stats(BaseModel):
    """Statistiques globales"""
    total_events: int
    total_categories: int
    total_cities: int
    free_events: int
    weekend_events: int
    by_category: List[dict]
    by_arrondissement: List[dict]
    by_season: List[dict]


class SearchResult(BaseModel):
    """Résultat de recherche"""
    id: int
    title: str
    description: Optional[str] = None
    event_date: date
    category_name: Optional[str] = None
    rank: float
    
    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    mongodb: bool
    postgresql: bool
    timestamp: datetime