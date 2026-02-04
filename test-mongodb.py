"""
Test rapide de connexion MongoDB
"""

import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.mongodb_client import MongoDBClient


def quick_test():
    """Test rapide de connexion"""
    print("🧪 Test de connexion MongoDB...\n")
    
    client = MongoDBClient()
    
    if client.connect():
        print("✅ Connexion réussie !")
        
        db = client.get_database()
        print(f"📂 Base de données : {db.name}")
        
        # Tester l'insertion d'un document test
        test_collection = db["test"]
        result = test_collection.insert_one({"test": "ok"})
        print(f"✅ Insertion test réussie : {result.inserted_id}")
        
        # Supprimer le document test
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Suppression test réussie")
        
        client.disconnect()
        print("\n🎉 MongoDB est opérationnel !")
        return True
    else:
        print("\n❌ Impossible de se connecter à MongoDB")
        print("\n💡 Solutions :")
        print("   1. Démarrer MongoDB avec Docker :")
        print("      docker run -d -p 27017:27017 --name mongodb mongo:6")
        print("   2. Ou installer MongoDB localement")
        return False


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)