#!/usr/bin/env python3
# storage/mongodb_client.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    def __init__(self):
        self.uri = "mongodb://localhost:27017/"
        self.client = MongoClient(self.uri)
        self.database_name = "cultural_events"
        self.db = self.client[self.database_name]
        self.raw_collection_name = "events_raw"
        self.enriched_collection_name = "events_enriched"
        self.raw = self.db[self.raw_collection_name]
        self.enriched = self.db[self.enriched_collection_name]
    
    def connect(self):
        try:
            self.client.admin.command('ping')
            print('✅ MongoDB connecté')
            return True
        except ConnectionFailure:
            print('❌ MongoDB indisponible')
            return False
    
    def create_indexes(self):
        self.raw.create_index([("location.coordinates", "2dsphere")])
        self.raw.create_index([("dates.start", 1)])
        self.raw.create_index([("title", "text"), ("description", "text")])
        print('✅ Index: géo, chrono, texte')
    
    def get_database(self):
        return self.db
    
    def disconnect(self):
        self.client.close()


def init_mongodb():
    print("=" * 70)
    print("🚀 INITIALISATION DE MONGODB")
    print("=" * 70)
    
    # Connexion CORRIGÉE
    client = MongoDBClient()
    
    # TEST CORRECT (pas de bool() sur database)
    if client.connect():  
        try:
            # Collections
            print("\n📁 Vérification collections...")
            raw_count = client.raw.count_documents({})
            enriched_count = client.enriched.count_documents({})
            print(f"   RAW ({client.raw_collection_name}): {raw_count} docs")
            print(f"   ENRICHED: {enriched_count} docs")
            
            # Index
            client.create_indexes()
            
            print("\n✅ INITIALISATION TERMINÉE")
            print("💡 Lancez: python collectors/paris_collector.py")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
        finally:
            client.disconnect()
    else:
        print("❌ Connexion échouée")
        return False

if __name__ == "__main__":
    init_mongodb()
