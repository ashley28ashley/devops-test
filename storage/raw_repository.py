"""
Repository RAW - Insertion des événements bruts dans MongoDB
Adapté à votre MongoDBClient existant
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pymongo.errors import DuplicateKeyError, BulkWriteError

# ✅ IMPORT DIRECT de votre MongoDBClient
from mongodb_client import MongoDBClient

class RawEventRepository:
    """Gestionnaire d'insertion des événements RAW dans MongoDB"""
    
    def __init__(self):
        self.client = MongoDBClient()
        self.collection = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Établit la connexion et récupère la collection RAW"""
        if self.client.connect():
            self.collection = self.client.raw  # ✅ Utilise votre attribut .raw
            self.is_connected = True
            print("✅ Connecté à events_raw")
            return True
        print("❌ Échec connexion MongoDB")
        return False
    
    def insert_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Insère un seul événement"""
        if not self.is_connected:
            return None
        
        try:
            result = self.collection.insert_one(event)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None  # Doublon existant
        except Exception as e:
            print(f"❌ Insertion erreur: {e}")
            return None
    
    def insert_many_events(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Insertion bulk optimisée avec gestion doublons"""
        stats = {"inserted": 0, "duplicates": 0, "errors": 0}
        
        if not self.is_connected or not events:
            return stats
        
        try:
            # ✅ ordered=False = continue malgré doublons
            result = self.collection.insert_many(events, ordered=False)
            stats["inserted"] = len(result.inserted_ids)
            print(f"✅ {stats['inserted']} événements insérés")
            
        except BulkWriteError as bwe:
            stats["inserted"] = bwe.details.get("nInserted", 0)
            duplicates = sum(1 for e in bwe.details.get("writeErrors", []) if e.get("code") == 11000)
            stats["duplicates"] = duplicates
            stats["errors"] = len(bwe.details.get("writeErrors", [])) - duplicates
            
        except Exception as e:
            print(f"❌ Bulk insert erreur: {e}")
            stats["errors"] = len(events)
        
        return stats
    
    def load_from_json_file(self, filepath: str = "events_raw.json") -> Dict[str, int]:
        """Charge ET valide votre fichier JSON"""
        print(f"📂 Chargement: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"❌ Fichier introuvable: {filepath}")
            return {"inserted": 0, "duplicates": 0, "errors": 1}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            if not isinstance(events, list):
                print("❌ JSON doit être une liste")
                return {"inserted": 0, "duplicates": 0, "errors": 1}
            
            print(f"📊 {len(events)} événements détectés")
            
            # Validation + nettoyage
            valid_events = []
            invalid = 0
            
            for event in events:
                if self._validate_event(event):
                    valid_events.append(event)
                else:
                    invalid += 1
            
            if invalid > 0:
                print(f"⚠️ {invalid} événements ignorés (structure invalide)")
            
            print(f"✅ {len(valid_events)} événements valides")
            
            # Bulk insert
            stats = self.insert_many_events(valid_events)
            return stats
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide: {e}")
            return {"inserted": 0, "duplicates": 0, "errors": 1}
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return {"inserted": 0, "duplicates": 0, "errors": 1}
    
    def _validate_event(self, event: Dict[str, Any]) -> bool:
        """Validation structure événement"""
        try:
            # Structure attendue
            required_fields = ["source", "fetched_at", "raw_hash", "payload"]
            
            if not all(k in event for k in required_fields):
                return False
            
            # Vérifier que payload existe et est un dict
            if not isinstance(event["payload"], dict):
                return False
            
            # Le payload doit avoir au minimum un titre ou un id
            payload = event["payload"]
            if "title" not in payload and "id" not in payload:
                return False
            
            return True
            
        except:
            return False
    
    def count_events(self, filter_query: Optional[Dict] = None) -> int:
        """Compte les événements"""
        if not self.is_connected:
            return 0
        return self.collection.count_documents(filter_query or {})
    
    def get_events(self, limit: int = 10, skip: int = 0) -> List[Dict]:
        """Récupère des événements avec pagination"""
        if not self.is_connected:
            return []
        return list(self.collection.find().skip(skip).limit(limit))
    
    def get_stats(self) -> Dict:
        """Statistiques de la collection"""
        if not self.is_connected:
            return {}
        
        total = self.count_events()
        
        # Statistiques par source
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        sources_stats = list(self.collection.aggregate(pipeline))
        
        return {
            "total": total,
            "sources": sources_stats
        }
    
    def disconnect(self):
        """Fermeture propre"""
        if self.is_connected:
            self.client.disconnect()
            self.is_connected = False


def main():
    """🚀 Point d'entrée - Charge events_raw.json"""
    print("=" * 70)
    print("💾 CHARGEMENT DES ÉVÉNEMENTS DANS MONGODB")
    print("=" * 70 + "\n")
    
    repo = RawEventRepository()
    
    if not repo.connect():
        print("\n❌ Impossible de se connecter à MongoDB")
        print("💡 Assurez-vous que MongoDB est démarré:")
        print("   docker ps")
        return
    
    # 📂 Charger le fichier
    filepath = "events_raw.json"
    stats = repo.load_from_json_file(filepath)
    
    # 📊 Résultats détaillés
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS DE L'INSERTION")
    print("=" * 70)
    print(f"\n✅ Insérés:    {stats['inserted']} événements")
    print(f"🔄 Doublons:   {stats['duplicates']} événements")
    print(f"❌ Erreurs:    {stats['errors']} événements")
    
    total_processed = stats['inserted'] + stats['duplicates'] + stats['errors']
    if total_processed > 0:
        success_rate = (stats['inserted'] / total_processed) * 100
        print(f"\n📈 Taux d'insertion: {success_rate:.1f}%")
    
    # Statistiques de la collection
    print("\n" + "=" * 70)
    print("🗂️ CONTENU DE LA COLLECTION")
    print("=" * 70)
    
    total = repo.count_events()
    print(f"\n📄 Total d'événements en base: {total}")
    
    # Aperçu des 3 premiers
    if total > 0:
        print(f"\n📋 Exemples d'événements (3 premiers):")
        events = repo.get_events(limit=3)
        
        for i, event in enumerate(events, 1):
            payload = event.get("payload", {})
            title = payload.get("title", "Sans titre")
            source = event.get("source", "Unknown")
            
            print(f"\n   {i}. {title}")
            print(f"      Source: {source}")
            print(f"      Hash: {event.get('raw_hash', 'N/A')[:16]}...")
    
    # Stats par source
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES PAR SOURCE")
    print("=" * 70 + "\n")
    
    collection_stats = repo.get_stats()
    for stat in collection_stats.get("sources", []):
        source = stat["_id"]
        count = stat["count"]
        print(f"   • {source}: {count} événements")
    
    repo.disconnect()
    print("\n✅ Processus terminé avec succès\n")


if __name__ == "__main__":
    main()