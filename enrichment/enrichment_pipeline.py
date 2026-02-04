
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Dict, List
from bson import ObjectId
import logging

from storage.mongodb_client import MongoDBClient
from enrichment.geocoding import GeocodingEnricher
from enrichment.categorization import CategorizationEnricher
from enrichment.date_processor import DateEnricher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    """Pipeline complet d'enrichissement"""
    
    def __init__(self):
        self.client = MongoDBClient()
        self.raw_collection = None
        self.enriched_collection = None
        
        # Initialiser les enrichisseurs
        self.geo_enricher = GeocodingEnricher()
        self.cat_enricher = CategorizationEnricher()
        self.date_enricher = DateEnricher()
        
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connexion à MongoDB"""
        if self.client.connect():
            self.raw_collection = self.client.raw
            self.enriched_collection = self.client.enriched
            self.is_connected = True
            return True
        return False
    
    def enrich_event(self, raw_event: Dict) -> Dict:
        """Enrichit un seul événement"""
        enriched_data = {}
        
        try:
            # 1. Géocodage
            logger.debug("Enrichissement géographique...")
            geo_data = self.geo_enricher.enrich(raw_event)
            enriched_data.update(geo_data)
            
            # 2. Catégorisation
            logger.debug("Catégorisation...")
            cat_data = self.cat_enricher.enrich(raw_event)
            enriched_data.update(cat_data)
            
            # 3. Dates
            logger.debug("Parsing des dates...")
            date_data = self.date_enricher.enrich(raw_event)
            enriched_data.update(date_data)
            
            # 4. Enrichissements additionnels
            enriched_data["is_free"] = self._check_if_free(raw_event)
            enriched_data["accessibility_score"] = self._calculate_accessibility(enriched_data)
            
        except Exception as e:
            logger.error(f"Erreur enrichissement: {e}")
            raise
        
        return enriched_data
    
    def _check_if_free(self, event: Dict) -> bool:
        """Détermine si l'événement est gratuit"""
        payload = event.get("payload", {})
        price_info = payload.get("price", {})
        
        if isinstance(price_info, dict):
            price_type = price_info.get("type", "").lower()
            price_detail = str(price_info.get("detail", "")).lower()
            
            return "gratuit" in price_type or "gratuit" in price_detail or "free" in price_type
        
        return False
    
    def _calculate_accessibility(self, enriched_data: Dict) -> float:
        """Calcule un score d'accessibilité (0-1)"""
        score = 0.0
        
        # +0.3 si gratuit
        if enriched_data.get("is_free"):
            score += 0.3
        
        # +0.2 si proche du centre
        distance = enriched_data.get("distance_center")
        if distance is not None:
            if distance < 2:
                score += 0.2
            elif distance < 5:
                score += 0.1
        
        # +0.3 si géocodé (accessible)
        if enriched_data.get("geocoded"):
            score += 0.3
        
        # +0.2 si weekend
        if enriched_data.get("is_weekend"):
            score += 0.2
        
        return round(min(score, 1.0), 2)
    
    def process_all_events(self, limit: Optional[int] = None) -> Dict:
        """Enrichit tous les événements RAW"""
        if not self.is_connected:
            logger.error("Pas de connexion MongoDB")
            return {"processed": 0, "success": 0, "failed": 0}
        
        stats = {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        try:
            # Récupérer les événements RAW
            query = {}
            cursor = self.raw_collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
            
            total = self.raw_collection.count_documents(query)
            if limit:
                total = min(total, limit)
            
            logger.info(f"Enrichissement de {total} événements...")
            
            for i, raw_event in enumerate(cursor, 1):
                try:
                    raw_id = raw_event["_id"]
                    
                    # Vérifier si déjà enrichi
                    existing = self.enriched_collection.find_one({"raw_id": raw_id})
                    if existing:
                        stats["skipped"] += 1
                        continue
                    
                    # Enrichir
                    enriched_data = self.enrich_event(raw_event)
                    
                    # Créer le document enriched
                    enriched_doc = {
                        "raw_id": raw_id,
                        "status": "success",
                        "enriched_at": datetime.utcnow(),
                        "data": enriched_data,
                        "error": None
                    }
                    
                    # Insérer
                    self.enriched_collection.insert_one(enriched_doc)
                    
                    stats["success"] += 1
                    stats["processed"] += 1
                    
                    # Afficher progression
                    if i % 50 == 0:
                        progress = (i / total) * 100
                        logger.info(f"⏳ Progression: {i}/{total} ({progress:.1f}%)")
                
                except Exception as e:
                    logger.error(f"Erreur événement {i}: {e}")
                    
                    # Insérer un document d'erreur
                    try:
                        enriched_doc = {
                            "raw_id": raw_event["_id"],
                            "status": "failed",
                            "enriched_at": datetime.utcnow(),
                            "data": {},
                            "error": {"message": str(e)}
                        }
                        self.enriched_collection.insert_one(enriched_doc)
                    except:
                        pass
                    
                    stats["failed"] += 1
                    stats["processed"] += 1
        
        except Exception as e:
            logger.error(f"Erreur pipeline: {e}")
        
        return stats
    
    def get_enrichment_stats(self) -> Dict:
        """Statistiques de la collection enriched"""
        if not self.is_connected:
            return {}
        
        total = self.enriched_collection.count_documents({})
        success = self.enriched_collection.count_documents({"status": "success"})
        failed = self.enriched_collection.count_documents({"status": "failed"})
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 2) if total > 0 else 0
        }
    
    def disconnect(self):
        """Fermeture propre"""
        if self.is_connected:
            self.geo_enricher.close()
            self.client.disconnect()
            self.is_connected = False


def main():
    """🚀 Point d'entrée principal"""
    print("=" * 70)
    print("🎨 PIPELINE D'ENRICHISSEMENT")
    print("=" * 70 + "\n")
    
    pipeline = EnrichmentPipeline()
    
    if not pipeline.connect():
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    # Vérifier les données RAW
    raw_count = pipeline.raw_collection.count_documents({})
    print(f"📊 Événements RAW disponibles: {raw_count}")
    
    if raw_count == 0:
        print("⚠️ Aucun événement à enrichir")
        print("💡 Lancez d'abord: python storage/raw_repository.py")
        pipeline.disconnect()
        return
    
    # Vérifier si déjà enrichis
    enriched_count = pipeline.enriched_collection.count_documents({})
    print(f"📊 Événements déjà enrichis: {enriched_count}")
    
    if enriched_count >= raw_count:
        print("\n✅ Tous les événements sont déjà enrichis!")
        stats = pipeline.get_enrichment_stats()
        print(f"\n📈 Statistiques:")
        print(f"   Total: {stats['total']}")
        print(f"   Succès: {stats['success']}")
        print(f"   Échecs: {stats['failed']}")
        print(f"   Taux de succès: {stats['success_rate']}%")
        pipeline.disconnect()
        return
    
    # Lancer l'enrichissement
    print(f"\n🚀 Lancement de l'enrichissement...\n")
    
    # Pour le test, limiter à 50 événements
    # Retirez limit=50 pour enrichir tous les événements
    stats = pipeline.process_all_events(limit=None)
    
    # Résultats
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS")
    print("=" * 70)
    print(f"\n✅ Traités:   {stats['processed']} événements")
    print(f"✅ Succès:    {stats['success']} événements")
    print(f"❌ Échecs:    {stats['failed']} événements")
    print(f"⏭️ Ignorés:   {stats['skipped']} événements (déjà enrichis)")
    
    if stats['processed'] > 0:
        success_rate = (stats['success'] / stats['processed']) * 100
        print(f"\n📈 Taux de succès: {success_rate:.1f}%")
    
    # Statistiques finales
    final_stats = pipeline.get_enrichment_stats()
    print("\n" + "=" * 70)
    print("📊 ÉTAT FINAL DE LA COLLECTION ENRICHED")
    print("=" * 70)
    print(f"\n📄 Total: {final_stats['total']} événements")
    print(f"✅ Succès: {final_stats['success']} événements")
    print(f"❌ Échecs: {final_stats['failed']} événements")
    print(f"📈 Taux global: {final_stats['success_rate']}%")
    
    # Exemples
    print("\n" + "=" * 70)
    print("📋 EXEMPLES D'ÉVÉNEMENTS ENRICHIS")
    print("=" * 70)
    
    examples = pipeline.enriched_collection.find({"status": "success"}).limit(3)
    
    for i, doc in enumerate(examples, 1):
        data = doc.get("data", {})
        raw_event = pipeline.raw_collection.find_one({"_id": doc["raw_id"]})
        title = raw_event.get("payload", {}).get("title", "Sans titre") if raw_event else "N/A"
        
        print(f"\n{i}. {title}")
        print(f"   📍 Position: {data.get('arrondissement', 'N/A')}")
        print(f"   🏷️ Catégorie: {data.get('main_category', 'N/A')}")
        if data.get('sub_category'):
            print(f"   🏷️ Sous-catégorie: {data['sub_category']}")
        print(f"   📅 Jour: {data.get('day_of_week_name', 'N/A')}")
        print(f"   🌦️ Saison: {data.get('season', 'N/A')}")
        print(f"   💰 Gratuit: {'Oui' if data.get('is_free') else 'Non'}")
        print(f("   ⭐ Accessibilité: {data.get('accessibility_score', 0)}/1"))
    
    pipeline.disconnect()
    print("\n✅ Enrichissement terminé avec succès!\n")


if __name__ == "__main__":
    main()