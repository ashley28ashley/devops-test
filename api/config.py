"""
Configuration et connexions pour l'API
"""

import os
from typing import Optional
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration des bases de données"""
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")  # Port Docker
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "cultural_events")
    
    @classmethod
    def get_postgres_dsn(cls) -> str:
        """Retourne le DSN PostgreSQL"""
        return f"host={cls.POSTGRES_HOST} port={cls.POSTGRES_PORT} dbname={cls.POSTGRES_DATABASE} user={cls.POSTGRES_USER} password={cls.POSTGRES_PASSWORD}"


@contextmanager
def get_db_connection():
    """Context manager pour connexion PostgreSQL"""
    conn = None
    try:
        dsn = DatabaseConfig.get_postgres_dsn()
        conn = psycopg.connect(dsn, row_factory=dict_row)
        yield conn
    except Exception as e:
        logger.error(f"Erreur connexion PostgreSQL: {e}")
        raise
    finally:
        if conn:
            conn.close()


def test_postgres_connection() -> bool:
    """Test la connexion PostgreSQL"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"PostgreSQL indisponible: {e}")
        return False


class APIConfig:
    """Configuration de l'API"""
    
    # API
    API_TITLE = "Cultural Events API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    API REST pour les événements culturels parisiens.
    
    ## Fonctionnalités
    
    * **Events** - Liste et détails des événements
    * **Search** - Recherche plein texte
    * **Stats** - Statistiques et analyses
    * **Categories** - Liste des catégories
    * **Cities** - Liste des villes
    
    ## Filtres disponibles
    
    * Par catégorie
    * Par ville/arrondissement
    * Par date (plage)
    * Gratuit uniquement
    * Weekend uniquement
    * Par saison
    """
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100