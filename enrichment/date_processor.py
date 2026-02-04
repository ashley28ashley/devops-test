
from datetime import datetime
from typing import Dict, Optional
import logging
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class DateEnricher:
    """Enrichissement temporel des événements"""
    
    def __init__(self):
        self.months_fr = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        
        self.days_fr = [
            "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"
        ]
        
        self.seasons = {
            (3, 20): "Printemps",
            (6, 21): "Été",
            (9, 22): "Automne",
            (12, 21): "Hiver"
        }
    
    def enrich(self, event: Dict) -> Dict:
        """Enrichit un événement avec données temporelles"""
        result = {
            "event_date": None,
            "event_datetime": None,
            "year": None,
            "month": None,
            "month_name": None,
            "day": None,
            "day_of_week": None,
            "day_of_week_name": None,
            "is_weekend": False,
            "season": None,
            "time_period": None,  # matin, après-midi, soir, nuit
            "duration_days": None,
            "is_multi_day": False
        }
        
        try:
            payload = event.get("payload", {})
            dates = payload.get("dates", {})
            
            # Parser la date de début
            start_date = self._parse_date(dates.get("start"))
            
            if start_date:
                result["event_datetime"] = start_date.isoformat()
                result["event_date"] = start_date.date().isoformat()
                result["year"] = start_date.year
                result["month"] = start_date.month
                result["month_name"] = self.months_fr[start_date.month - 1]
                result["day"] = start_date.day
                result["day_of_week"] = start_date.weekday() + 1  # 1=Lundi, 7=Dimanche
                result["day_of_week_name"] = self.days_fr[start_date.weekday()]
                result["is_weekend"] = start_date.weekday() >= 5  # Samedi=5, Dimanche=6
                result["season"] = self._get_season(start_date)
                result["time_period"] = self._get_time_period(start_date)
                
                # Parser la date de fin
                end_date = self._parse_date(dates.get("end"))
                
                if end_date and end_date > start_date:
                    duration = (end_date.date() - start_date.date()).days
                    result["duration_days"] = duration
                    result["is_multi_day"] = duration > 0
        
        except Exception as e:
            logger.error(f"Erreur parsing date: {e}")
        
        return result
    
    def _parse_date(self, date_str) -> Optional[datetime]:
        """Parse une date string en datetime"""
        if not date_str:
            return None
        
        try:
            # Essayer plusieurs formats
            if isinstance(date_str, datetime):
                return date_str
            
            if isinstance(date_str, str):
                # Parser avec dateutil (très flexible)
                return date_parser.parse(date_str)
        
        except Exception as e:
            logger.debug(f"Impossible de parser la date '{date_str}': {e}")
        
        return None
    
    def _get_season(self, date: datetime) -> str:
        """Détermine la saison"""
        month = date.month
        day = date.day
        
        if (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
            return "Printemps"
        elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 22):
            return "Été"
        elif (month == 9 and day >= 22) or month in [10, 11] or (month == 12 and day < 21):
            return "Automne"
        else:
            return "Hiver"
    
    def _get_time_period(self, date: datetime) -> str:
        """Détermine la période de la journée"""
        hour = date.hour
        
        if 5 <= hour < 12:
            return "Matin"
        elif 12 <= hour < 18:
            return "Après-midi"
        elif 18 <= hour < 23:
            return "Soir"
        else:
            return "Nuit"


if __name__ == "__main__":
    print("🧪 TEST DATES\n")
    
    enricher = DateEnricher()
    
    # Test 1 : Événement avec date complète
    event1 = {
        "payload": {
            "title": "Concert",
            "dates": {
                "start": "2025-02-14T20:00:00",
                "end": "2025-02-14T23:00:00"
            }
        }
    }
    
    result1 = enricher.enrich(event1)
    print("Test 1 : Concert du soir")
    print(f"✅ Date: {result1['event_date']}")
    print(f"✅ Jour: {result1['day_of_week_name']}")
    print(f"✅ Mois: {result1['month_name']}")
    print(f"✅ Saison: {result1['season']}")
    print(f"✅ Période: {result1['time_period']}")
    print(f"✅ Weekend: {result1['is_weekend']}\n")
    
    # Test 2 : Festival multi-jours
    event2 = {
        "payload": {
            "title": "Festival",
            "dates": {
                "start": "2025-07-10T10:00:00",
                "end": "2025-07-13T23:00:00"
            }
        }
    }
    
    result2 = enricher.enrich(event2)
    print("Test 2 : Festival multi-jours")
    print(f"✅ Date début: {result2['event_date']}")
    print(f"✅ Durée: {result2['duration_days']} jours")
    print(f"✅ Multi-jours: {result2['is_multi_day']}")
    print(f"✅ Saison: {result2['season']}\n")
    
    print("✅ Tests terminés")