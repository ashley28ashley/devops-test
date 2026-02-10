"""
ETL - Transformer
Transforme les données MongoDB enriched vers format SQL
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforme les données MongoDB vers PostgreSQL"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def transform_event(self, raw_doc: Dict, enriched_doc: Dict) -> Optional[Dict]:
        """
        Transforme un événement MongoDB vers format SQL
        
        Args:
            raw_doc: Document de events_raw
            enriched_doc: Document de events_enriched
            
        Returns:
            dict: Données formatées pour SQL ou None si erreur
        """
        try:
            payload = raw_doc.get("payload", {})
            enriched_data = enriched_doc.get("data", {})
            
            # Données de base
            event_data = {
                # Identification
                "raw_id": str(raw_doc["_id"]),
                "source": raw_doc.get("source", "unknown"),
                
                # Titre et description
                "title": self._clean_text(payload.get("title"), max_length=500),
                "description": self._clean_text(payload.get("description")),
                
                # Adresse
                "address_street": self._extract_address_street(payload),
                "address_name": self._extract_address_name(payload),
                "zipcode": self._extract_zipcode(payload, enriched_data),
                "arrondissement": enriched_data.get("arrondissement"),
                
                # Géolocalisation
                "latitude": enriched_data.get("latitude"),
                "longitude": enriched_data.get("longitude"),
                "distance_center": enriched_data.get("distance_center"),
                "geocoded": enriched_data.get("geocoded", False),
                
                # Dates
                "event_date": self._parse_date(enriched_data.get("event_date")),
                "event_datetime": self._parse_datetime(enriched_data.get("event_datetime")),
                "year": enriched_data.get("year"),
                "month": enriched_data.get("month"),
                "day": enriched_data.get("day"),
                "day_of_week": enriched_data.get("day_of_week"),
                "day_of_week_name": enriched_data.get("day_of_week_name"),
                "month_name": enriched_data.get("month_name"),
                "season": enriched_data.get("season"),
                "time_period": enriched_data.get("time_period"),
                "is_weekend": enriched_data.get("is_weekend", False),
                "is_multi_day": enriched_data.get("is_multi_day", False),
                "duration_days": enriched_data.get("duration_days"),
                
                # Prix
                "price_type": self._extract_price_type(payload),
                "price_detail": self._extract_price_detail(payload),
                "is_free": enriched_data.get("is_free", False),
                "accessibility_score": enriched_data.get("accessibility_score"),
                
                # Contact
                "contact_url": self._extract_contact_url(payload),
                "contact_phone": self._extract_contact_phone(payload),
                "contact_email": self._extract_contact_email(payload),
            }
            
            # Ville (à résoudre via lookup)
            city_name = enriched_data.get("city") or payload.get("address", {}).get("city", "Paris")
            event_data["city_name"] = city_name
            
            # Catégories (à insérer dans table de liaison)
            event_data["main_category"] = enriched_data.get("main_category", "Autre")
            event_data["sub_category"] = enriched_data.get("sub_category")
            event_data["category_confidence"] = enriched_data.get("confidence", 0.0)
            
            self.processed_count += 1
            return event_data
            
        except Exception as e:
            logger.error(f"Erreur transformation: {e}")
            self.error_count += 1
            return None
    
    def _clean_text(self, text: any, max_length: Optional[int] = None) -> Optional[str]:
        """Nettoie un texte pour SQL"""
        if not text:
            return None
        
        text_str = str(text).strip()
        
        if not text_str:
            return None
        
        if max_length and len(text_str) > max_length:
            text_str = text_str[:max_length]
        
        return text_str
    
    def _extract_address_street(self, payload: Dict) -> Optional[str]:
        """Extrait la rue de l'adresse"""
        address = payload.get("address", {})
        if isinstance(address, dict):
            return self._clean_text(address.get("street"), max_length=255)
        return None
    
    def _extract_address_name(self, payload: Dict) -> Optional[str]:
        """Extrait le nom du lieu"""
        address = payload.get("address", {})
        if isinstance(address, dict):
            return self._clean_text(address.get("name"), max_length=255)
        return None
    
    def _extract_zipcode(self, payload: Dict, enriched_data: Dict) -> Optional[str]:
        """Extrait le code postal"""
        # Priorité à l'enrichissement
        zipcode = enriched_data.get("postcode")
        if zipcode:
            return str(zipcode)[:10]
        
        # Sinon payload
        address = payload.get("address", {})
        if isinstance(address, dict):
            zipcode = address.get("zipcode")
            if zipcode:
                return str(zipcode)[:10]
        
        return None
    
    def _extract_price_type(self, payload: Dict) -> Optional[str]:
        """Extrait le type de prix"""
        price = payload.get("price", {})
        if isinstance(price, dict):
            return self._clean_text(price.get("type"), max_length=50)
        return None
    
    def _extract_price_detail(self, payload: Dict) -> Optional[str]:
        """Extrait le détail du prix"""
        price = payload.get("price", {})
        if isinstance(price, dict):
            return self._clean_text(price.get("detail"), max_length=255)
        return None
    
    def _extract_contact_url(self, payload: Dict) -> Optional[str]:
        """Extrait l'URL de contact"""
        contact = payload.get("contact", {})
        if isinstance(contact, dict):
            return self._clean_text(contact.get("url"), max_length=500)
        return None
    
    def _extract_contact_phone(self, payload: Dict) -> Optional[str]:
        """Extrait le téléphone"""
        contact = payload.get("contact", {})
        if isinstance(contact, dict):
            return self._clean_text(contact.get("phone"), max_length=50)
        return None
    
    def _extract_contact_email(self, payload: Dict) -> Optional[str]:
        """Extrait l'email"""
        contact = payload.get("contact", {})
        if isinstance(contact, dict):
            return self._clean_text(contact.get("email"), max_length=255)
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse une date ISO vers format SQL"""
        if not date_str:
            return None
        
        try:
            # Format ISO: 2025-02-14
            if isinstance(date_str, str) and len(date_str) >= 10:
                return date_str[:10]
        except:
            pass
        
        return None
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[str]:
        """Parse un datetime ISO vers format SQL"""
        if not datetime_str:
            return None
        
        try:
            # Format ISO: 2025-02-14T20:00:00
            if isinstance(datetime_str, str):
                # PostgreSQL accepte le format ISO directement
                return datetime_str
        except:
            pass
        
        return None
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de transformation"""
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
            "success_rate": round(
                (self.processed_count / (self.processed_count + self.error_count) * 100)
                if (self.processed_count + self.error_count) > 0 else 0,
                2
            )
        }


if __name__ == "__main__":
    # Test
    print("🧪 TEST TRANSFORMER\n")
    
    transformer = DataTransformer()
    
    # Données de test
    raw_doc = {
        "_id": "507f1f77bcf86cd799439011",
        "source": "paris_open_data",
        "payload": {
            "title": "Concert de Jazz",
            "description": "Un concert exceptionnel",
            "address": {
                "street": "12 rue des Arts",
                "zipcode": "75004",
                "city": "Paris"
            },
            "price": {
                "type": "payant",
                "detail": "15€"
            },
            "contact": {
                "url": "https://example.com"
            }
        }
    }
    
    enriched_doc = {
        "data": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "arrondissement": "4e",
            "event_date": "2025-02-14",
            "event_datetime": "2025-02-14T20:00:00",
            "season": "Hiver",
            "main_category": "Musique",
            "sub_category": "Jazz",
            "is_free": False,
            "accessibility_score": 0.7
        }
    }
    
    result = transformer.transform_event(raw_doc, enriched_doc)
    
    if result:
        print("✅ Transformation réussie:\n")
        for key, value in result.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Transformation échouée")
    
    print(f"\n📊 Stats: {transformer.get_stats()}")