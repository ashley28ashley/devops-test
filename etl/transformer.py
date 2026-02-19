from typing import Dict, Optional
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
        """

        try:
            payload = raw_doc.get("payload", {})
            enriched_data = enriched_doc.get("data", {})

            # -----------------------------
            # 1. Construction de base
            # -----------------------------
            event_data = {
                "raw_id": str(raw_doc["_id"]),
                "source": raw_doc.get("source", "unknown"),

                "title": self._clean_text(payload.get("title"), max_length=500),
                "description": self._clean_text(payload.get("description")),

                "address_street": self._extract_address_street(payload),
                "address_name": self._extract_address_name(payload),
                "zipcode": self._extract_zipcode(payload, enriched_data),
                "arrondissement": enriched_data.get("arrondissement"),

                "latitude": enriched_data.get("latitude"),
                "longitude": enriched_data.get("longitude"),
                "distance_center": enriched_data.get("distance_center"),
                "geocoded": enriched_data.get("geocoded", False),

                # Valeurs brutes (seront recalculées plus bas)
                "event_date": None,
                "event_datetime": None,
                "year": None,
                "month": None,
                "day": None,
                "day_of_week": None,
                "day_of_week_name": None,
                "month_name": None,
                "season": None,
                "time_period": None,
                "is_weekend": False,
                "is_multi_day": enriched_data.get("is_multi_day", False),
                "duration_days": enriched_data.get("duration_days"),

                "price_type": self._extract_price_type(payload),
                "price_detail": self._extract_price_detail(payload),
                "is_free": enriched_data.get("is_free", False),
                "accessibility_score": enriched_data.get("accessibility_score"),

                "contact_url": self._extract_contact_url(payload),
                "contact_phone": self._extract_contact_phone(payload),
                "contact_email": self._extract_contact_email(payload),
            }

            # -----------------------------
            # 2. Résolution de la ville
            # -----------------------------
            city_name = enriched_data.get("city") or payload.get("address", {}).get("city", "Paris")
            event_data["city_name"] = city_name

            # -----------------------------
            # 3. Catégories
            # -----------------------------
            event_data["main_category"] = enriched_data.get("main_category", "Autre")
            event_data["sub_category"] = enriched_data.get("sub_category")
            event_data["category_confidence"] = enriched_data.get("confidence", 0.0)

            # -----------------------------
            # 4. CALCUL AUTOMATIQUE DES DATES
            # -----------------------------
            raw_dt = (
                enriched_data.get("event_datetime")
                or enriched_data.get("event_date")
                or payload.get("date")
            )

            if raw_dt:
                try:
                    dt = datetime.fromisoformat(raw_dt)

                    event_data["event_datetime"] = dt.isoformat()
                    event_data["event_date"] = dt.date().isoformat()

                    event_data["year"] = dt.year
                    event_data["month"] = dt.month
                    event_data["day"] = dt.day

                    event_data["day_of_week"] = dt.weekday()
                    event_data["day_of_week_name"] = dt.strftime("%A")
                    event_data["month_name"] = dt.strftime("%B")

                    event_data["is_weekend"] = dt.weekday() >= 5

                    m = dt.month
                    if m in (12, 1, 2):
                        event_data["season"] = "Hiver"
                    elif m in (3, 4, 5):
                        event_data["season"] = "Printemps"
                    elif m in (6, 7, 8):
                        event_data["season"] = "Été"
                    else:
                        event_data["season"] = "Automne"

                    hour = dt.hour
                    if hour < 12:
                        event_data["time_period"] = "Matin"
                    elif hour < 18:
                        event_data["time_period"] = "Après-midi"
                    else:
                        event_data["time_period"] = "Soir"

                except Exception as e:
                    logger.error(f"Erreur parsing datetime: {e}")

            self.processed_count += 1
            return event_data

        except Exception as e:
            logger.error(f"Erreur transformation: {e}")
            self.error_count += 1
            return None

    # -------------------------------------------------
    # MÉTHODES UTILITAIRES (inchangées)
    # -------------------------------------------------

    def _clean_text(self, text, max_length=None):
        if not text:
            return None
        text = str(text).strip()
        if not text:
            return None
        if max_length and len(text) > max_length:
            return text[:max_length]
        return text

    def _extract_address_street(self, payload):
        address = payload.get("address", {})
        return self._clean_text(address.get("street"), 255) if isinstance(address, dict) else None

    def _extract_address_name(self, payload):
        address = payload.get("address", {})
        return self._clean_text(address.get("name"), 255) if isinstance(address, dict) else None

    def _extract_zipcode(self, payload, enriched_data):
        zipcode = enriched_data.get("postcode")
        if zipcode:
            return str(zipcode)[:10]
        address = payload.get("address", {})
        if isinstance(address, dict):
            zipcode = address.get("zipcode")
            if zipcode:
                return str(zipcode)[:10]
        return None

    def _extract_price_type(self, payload):
        price = payload.get("price", {})
        return self._clean_text(price.get("type"), 50) if isinstance(price, dict) else None

    def _extract_price_detail(self, payload):
        price = payload.get("price", {})
        return self._clean_text(price.get("detail"), 255) if isinstance(price, dict) else None

    def _extract_contact_url(self, payload):
        contact = payload.get("contact", {})
        return self._clean_text(contact.get("url"), 500) if isinstance(contact, dict) else None

    def _extract_contact_phone(self, payload):
        contact = payload.get("contact", {})
        return self._clean_text(contact.get("phone"), 50) if isinstance(contact, dict) else None

    def _extract_contact_email(self, payload):
        contact = payload.get("contact", {})
        return self._clean_text(contact.get("email"), 255) if isinstance(contact, dict) else None

    def get_stats(self):
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
        }