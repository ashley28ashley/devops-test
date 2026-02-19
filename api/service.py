"""
Service de gestion des événements
"""

from typing import List, Optional, Dict, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)


class EventService:
    """Service pour les opérations sur les événements"""

    @staticmethod
    def get_events(
        conn,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        city: Optional[str] = None,
        arrondissement: Optional[str] = None,
        is_free: Optional[bool] = None,
        is_weekend: Optional[bool] = None,
        season: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """Récupère la liste des événements avec filtres et pagination"""

        cursor = conn.cursor()

        # Sélection complète des colonnes utiles
        query = """
            SELECT 
                e.id,
                e.title,
                e.description,
                e.event_date,
                e.event_datetime,
                e.event_end_date,
                e.year,
                e.month,
                e.day,
                e.day_of_week,
                e.day_of_week_name,
                e.month_name,
                e.season,
                e.time_period,
                e.is_weekend,
                e.is_multi_day,
                e.duration_days,
                e.is_free,
                e.price_type,
                e.price_detail,
                e.address_street,
                e.address_name,
                e.zipcode,
                e.arrondissement,
                e.latitude,
                e.longitude,
                e.distance_center,
                e.contact_url,
                e.contact_phone,
                e.contact_email,
                c.name AS category_name,
                c.parent_category
            FROM events e
            LEFT JOIN event_categories ec 
                ON e.id = ec.event_id AND ec.is_primary = TRUE
            LEFT JOIN categories c 
                ON ec.category_id = c.id
            WHERE 1=1
        """

        params = []

        # Filtres
        if category:
            query += " AND c.name = %s"
            params.append(category)

        if city:
            query += " AND EXISTS (SELECT 1 FROM cities ci WHERE ci.id = e.city_id AND ci.name = %s)"
            params.append(city)

        if arrondissement:
            query += " AND e.arrondissement = %s"
            params.append(arrondissement)

        if is_free is not None:
            query += " AND e.is_free = %s"
            params.append(is_free)

        if is_weekend is not None:
            query += " AND e.is_weekend = %s"
            params.append(is_weekend)

        if season:
            query += " AND e.season = %s"
            params.append(season)

        if date_from:
            query += " AND e.event_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND e.event_date <= %s"
            params.append(date_to)

        # Total
        count_query = f"SELECT COUNT(*) as total FROM ({query}) AS subq"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Pagination
        query += " ORDER BY COALESCE(e.event_date, e.event_datetime), e.id LIMIT %s OFFSET %s"
        offset = (page - 1) * page_size
        params.extend([page_size, offset])

        cursor.execute(query, params)
        events = cursor.fetchall()

        total_pages = (total + page_size - 1) // page_size

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "events": events
        }

    @staticmethod
    def get_event_by_id(conn, event_id: int) -> Optional[Dict]:
        """Récupère un événement par son ID"""

        cursor = conn.cursor()

        query = """
            SELECT 
                e.*,
                ci.name AS city_name,
                c.name AS category_name,
                c.parent_category
            FROM events e
            LEFT JOIN cities ci ON e.city_id = ci.id
            LEFT JOIN event_categories ec 
                ON e.id = ec.event_id AND ec.is_primary = TRUE
            LEFT JOIN categories c 
                ON ec.category_id = c.id
            WHERE e.id = %s
        """

        cursor.execute(query, (event_id,))
        return cursor.fetchone()

    @staticmethod
    def search_events(conn, query: str, limit: int = 20) -> List[Dict]:
        """Recherche plein texte dans les événements"""

        cursor = conn.cursor()

        sql = """
            SELECT * FROM search_events(%s)
            LIMIT %s
        """

        cursor.execute(sql, (query, limit))
        return cursor.fetchall()

    @staticmethod
    def get_categories(conn) -> List[Dict]:
        """Récupère toutes les catégories"""

        cursor = conn.cursor()

        query = """
            SELECT id, name, parent_category, event_count
            FROM categories
            ORDER BY event_count DESC, name
        """

        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_cities(conn) -> List[Dict]:
        """Récupère toutes les villes"""

        cursor = conn.cursor()

        query = """
            SELECT id, name, event_count
            FROM cities
            ORDER BY event_count DESC, name
        """

        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_stats(conn) -> Dict[str, Any]:
        """Récupère les statistiques globales"""

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM events")
        total_events = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM categories")
        total_categories = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM cities")
        total_cities = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM events WHERE is_free = TRUE")
        free_events = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM events WHERE is_weekend = TRUE")
        weekend_events = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT c.name, COUNT(e.id) as count
            FROM categories c
            LEFT JOIN event_categories ec ON c.id = ec.category_id AND ec.is_primary = TRUE
            LEFT JOIN events e ON ec.event_id = e.id
            GROUP BY c.name
            HAVING COUNT(e.id) > 0
            ORDER BY count DESC
            LIMIT 10
        """)
        by_category = cursor.fetchall()

        cursor.execute("""
            SELECT arrondissement, COUNT(*) as count
            FROM events
            WHERE arrondissement IS NOT NULL
            GROUP BY arrondissement
            ORDER BY count DESC
        """)
        by_arrondissement = cursor.fetchall()

        cursor.execute("""
            SELECT season, COUNT(*) as count
            FROM events
            WHERE season IS NOT NULL
            GROUP BY season
            ORDER BY count DESC
        """)
        by_season = cursor.fetchall()

        return {
            "total_events": total_events,
            "total_categories": total_categories,
            "total_cities": total_cities,
            "free_events": free_events,
            "weekend_events": weekend_events,
            "by_category": by_category,
            "by_arrondissement": by_arrondissement,
            "by_season": by_season
        }