# scripts/init_db.py - VERSION SANS LIMITE & CORRIGÉE ✅
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import json

print("=" * 60)
print("🚀 INIT MONGODB - ÉVÉNEMENTS PARIS 2026")
print("=" * 60)

def init_db():
    # Connexion directe
    client = MongoClient('mongodb://localhost:27017/')
    db = client['cultural_events']
    
    try:
        # Test connexion
        client.admin.command('ping')
        print("✅ MongoDB connecté")
        
        # Collections
        raw = db['events_raw']
        enriched = db['events_enriched']
        
        # Reset
        raw.delete_many({})
        enriched.delete_many({})
        print("✅ Collections créées/vidées")
        
        # INDEX GÉO Paris
        raw.create_index([("location.coordinates", "2dsphere")])
        raw.create_index([("dates.start", 1)])
        raw.create_index([("title", "text")])
        print("✅ Index: carte Paris + chrono + recherche")
        
        # IMPORT paste.txt (TOUS les événements)
        paste_path = os.path.join(os.path.dirname(__file__), "paste.txt")
        print(f"DEBUG: Chemin recherché = {paste_path}")
        
        if os.path.exists(paste_path):
            print("📄 paste.txt trouvé ! Chargement...")
            with open(paste_path, 'r', encoding='utf-8') as f:
                events = json.load(f)

            # Importation SANS limite
            for event in events:
                raw.insert_one(event)

            print(f"✅ {len(events)} événements importés dans MongoDB")
        else:
            print("ℹ️ paste.txt non trouvé - OK pour test")
        
        print("\n🎉 BASE PRÊTE!")
        print("🌐 API: uvicorn api.main:app --port 8000")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        client.close()
        print("🔌 Fermé")

if __name__ == "__main__":
    init_db()