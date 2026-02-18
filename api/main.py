"""
API REST FastAPI pour les événements culturels
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date, datetime
import logging

from api.config import APIConfig, get_db_connection, test_postgres_connection
from api.models import (
    EventList, EventDetail, CategoryBase, CityBase,
    Stats, SearchResult, HealthCheck
)
from api.service import EventService

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=APIConfig.API_TITLE,
    version=APIConfig.API_VERSION,
    description=APIConfig.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/", tags=["Health"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Cultural Events API",
        "version": APIConfig.API_VERSION,
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Vérifie l'état de l'API et des bases de données"""
    
    postgres_ok = test_postgres_connection()
    
    return HealthCheck(
        status="healthy" if postgres_ok else "degraded",
        mongodb=False,  # Non utilisé pour l'API
        postgresql=postgres_ok,
        timestamp=datetime.utcnow()
    )


# ============================================================
# EVENTS
# ============================================================

@app.get("/events", response_model=EventList, tags=["Events"])
async def get_events(
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    city: Optional[str] = Query(None, description="Filtrer par ville"),
    arrondissement: Optional[str] = Query(None, description="Filtrer par arrondissement (ex: 11e)"),
    is_free: Optional[bool] = Query(None, description="Uniquement les événements gratuits"),
    is_weekend: Optional[bool] = Query(None, description="Uniquement les événements du weekend"),
    season: Optional[str] = Query(None, description="Filtrer par saison (Printemps, Été, Automne, Hiver)"),
    date_from: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)")
):
    """
    Récupère la liste des événements avec pagination et filtres.
    """
    
    try:
        with get_db_connection() as conn:
            result = EventService.get_events(
                conn=conn,
                page=page,
                page_size=page_size,
                category=category,
                city=city,
                arrondissement=arrondissement,
                is_free=is_free,
                is_weekend=is_weekend,
                season=season,
                date_from=date_from,
                date_to=date_to
            )
            
            return EventList(**result)
    
    except Exception as e:
        logger.error(f"Erreur get_events: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


@app.get("/events/{event_id}", response_model=EventDetail, tags=["Events"])
async def get_event(event_id: int):
    """
    Récupère les détails complets d'un événement par son ID.
    
    """
    
    try:
        with get_db_connection() as conn:
            event = EventService.get_event_by_id(conn, event_id)
            
            if not event:
                raise HTTPException(status_code=404, detail="Événement non trouvé")
            
            return EventDetail(**event)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur get_event: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


# ============================================================
# SEARCH
# ============================================================

@app.get("/search", response_model=List[SearchResult], tags=["Search"])
async def search_events(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats")
):
    """
    Recherche plein texte dans les événements (titre et description).
    """
    
    try:
        with get_db_connection() as conn:
            results = EventService.search_events(conn, q, limit)
            return [SearchResult(**r) for r in results]
    
    except Exception as e:
        logger.error(f"Erreur search: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


# ============================================================
# CATEGORIES
# ============================================================

@app.get("/categories", response_model=List[CategoryBase], tags=["Categories"])
async def get_categories():
    """
    Récupère la liste de toutes les catégories.
    
    **Catégories disponibles :**
    - Musique (avec sous-catégories: Jazz, Classique, Rock, Pop, etc.)
    - Théâtre (Comédie, Drame, etc.)
    - Exposition (Art contemporain, Peinture, Photographie, etc.)
    - Danse
    - Cinéma
    - Conférence
    - Sport
    - Autre
    """
    
    try:
        with get_db_connection() as conn:
            categories = EventService.get_categories(conn)
            return [CategoryBase(**c) for c in categories]
    
    except Exception as e:
        logger.error(f"Erreur get_categories: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


# ============================================================
# CITIES
# ============================================================

@app.get("/cities", response_model=List[CityBase], tags=["Cities"])
async def get_cities():
    """
    Récupère la liste de toutes les villes avec le nombre d'événements.
    """
    
    try:
        with get_db_connection() as conn:
            cities = EventService.get_cities(conn)
            return [CityBase(**c) for c in cities]
    
    except Exception as e:
        logger.error(f"Erreur get_cities: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


# ============================================================
# STATS
# ============================================================

@app.get("/stats", response_model=Stats, tags=["Statistics"])
async def get_stats():
    """
    Récupère les statistiques globales.
    
    **Inclut :**
    - Nombre total d'événements
    - Nombre de catégories et villes
    - Événements gratuits et du weekend
    - Distribution par catégorie
    - Distribution par arrondissement
    - Distribution par saison
    """
    
    try:
        with get_db_connection() as conn:
            stats = EventService.get_stats(conn)
            return Stats(**stats)
    
    except Exception as e:
        logger.error(f"Erreur get_stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur")


# ============================================================
# STARTUP/SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'API"""
    logger.info("🚀 API démarrée")
    logger.info(f"📚 Documentation: http://localhost:8000/docs")
    
    # Test connexion PostgreSQL
    if test_postgres_connection():
        logger.info("✅ PostgreSQL connecté")
    else:
        logger.warning("⚠️ PostgreSQL indisponible")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt de l'API"""
    logger.info("👋 API arrêtée")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )