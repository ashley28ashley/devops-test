
import requests
import time
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeocodingEnricher:
    """Enrichissement géographique via API adresse.data.gouv.fr"""
    
    def __init__(self):
        self.api_url = "https://api-adresse.data.gouv.fr/search/"
        self.reverse_url = "https://api-adresse.data.gouv.fr/reverse/"
        self.session = requests.Session()
        self.cache = {}
    
    def enrich(self, event: Dict) -> Dict:
        """Enrichit un événement avec données géographiques"""
        result = {
            "latitude": None,
            "longitude": None,
            "geocoded": False,
            "address_quality": "unknown",
            "arrondissement": None,
            "postcode": None,
            "city": "Paris",
            "distance_center": None
        }
        
        try:
            payload = event.get("payload", {})
            
            # 1. Vérifier coordonnées existantes
            location = payload.get("location")
            if location and isinstance(location, list) and len(location) == 2:
                result["latitude"] = location[0]
                result["longitude"] = location[1]
                result["geocoded"] = True
                result["address_quality"] = "from_source"
                
                # Reverse geocoding
                reverse_data = self._reverse_geocode(location[0], location[1])
                if reverse_data:
                    result.update(reverse_data)
            
            # 2. Sinon, géocoder l'adresse
            else:
                address_data = payload.get("address", {})
                coords = self._geocode_address(address_data)
                
                if coords:
                    result["latitude"] = coords["lat"]
                    result["longitude"] = coords["lon"]
                    result["geocoded"] = True
                    result["address_quality"] = "geocoded"
                    
                    if coords.get("postcode"):
                        result["postcode"] = coords["postcode"]
                    if coords.get("city"):
                        result["city"] = coords["city"]
            
            # 3. Calculer distance au centre de Paris (Notre-Dame)
            if result["latitude"] and result["longitude"]:
                result["distance_center"] = self._calculate_distance(
                    result["latitude"], result["longitude"],
                    48.8534, 2.3488  # Notre-Dame
                )
                
                # Extraire arrondissement
                if result.get("postcode"):
                    result["arrondissement"] = self._extract_arrondissement(result["postcode"])
            
        except Exception as e:
            logger.error(f"Erreur géocodage: {e}")
        
        return result
    
    def _geocode_address(self, address_data: Dict) -> Optional[Dict]:
        """Géocode une adresse"""
        address_parts = []
        
        if isinstance(address_data, dict):
            street = address_data.get("street") or address_data.get("name")
            zipcode = address_data.get("zipcode")
            city = address_data.get("city", "Paris")
            
            if street:
                address_parts.append(street)
            if zipcode:
                address_parts.append(zipcode)
            if city:
                address_parts.append(city)
        
        if not address_parts:
            return None
        
        query = " ".join(address_parts)
        
        if query in self.cache:
            return self.cache[query]
        
        try:
            params = {"q": query, "limit": 1}
            response = self.session.get(self.api_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            if features:
                feature = features[0]
                geometry = feature.get("geometry", {})
                properties = feature.get("properties", {})
                
                result = {
                    "lon": geometry.get("coordinates", [None, None])[0],
                    "lat": geometry.get("coordinates", [None, None])[1],
                    "postcode": properties.get("postcode"),
                    "city": properties.get("city")
                }
                
                self.cache[query] = result
                time.sleep(0.1)  # Rate limiting
                
                return result
            
        except Exception as e:
            logger.warning(f"Géocodage échoué: {e}")
        
        return None
    
    def _reverse_geocode(self, lat: float, lon: float) -> Dict:
        """Reverse geocoding"""
        try:
            params = {"lat": lat, "lon": lon}
            response = self.session.get(self.reverse_url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            if features:
                properties = features[0].get("properties", {})
                return {
                    "postcode": properties.get("postcode"),
                    "city": properties.get("city")
                }
        except:
            pass
        
        return {}
    
    def _extract_arrondissement(self, postcode: str) -> Optional[str]:
        """Extrait l'arrondissement depuis le code postal"""
        if not postcode or not isinstance(postcode, str):
            return None
        
        if postcode.startswith("75") and len(postcode) == 5:
            arr_num = postcode[3:]
            if arr_num.isdigit():
                arr_int = int(arr_num)
                if 1 <= arr_int <= 20:
                    return f"{arr_int}e" if arr_int > 1 else "1er"
        
        return None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance en km (Haversine)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        lat1_rad, lat2_rad = radians(lat1), radians(lat2)
        delta_lat, delta_lon = radians(lat2 - lat1), radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)
    
    def close(self):
        """Ferme la session HTTP"""
        self.session.close()


if __name__ == "__main__":
    print("🧪 TEST GÉOCODAGE\n")
    
    enricher = GeocodingEnricher()
    
    event = {
        "payload": {
            "title": "Test",
            "location": [48.8566, 2.3522],
            "address": {"street": "Notre-Dame", "zipcode": "75004", "city": "Paris"}
        }
    }
    
    result = enricher.enrich(event)
    print(f"✅ Lat: {result['latitude']}")
    print(f"✅ Lon: {result['longitude']}")
    print(f"✅ Arrondissement: {result['arrondissement']}")
    print(f"✅ Distance: {result['distance_center']} km")
    
    enricher.close()