"""
ETL - Loader
Charge les données transformées dans PostgreSQL
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg as psycopg2
from psycopg import sql
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

from storage.mongodb_client import MongoDBClient
from etl.transformer import DataTransformer

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLLoader:
    """Charge les données dans PostgreSQL"""
    
    def __init__(self):
        # Configuration PostgreSQL (en dur pour éviter problème encodage .env)
        self.host = "localhost"
        self.port = "5433"
        self.database = "cultural_events"
        self.user = "postgres"
        self.password = "postgres"
        
        self.conn = None
        self.cursor = None
        
        # MongoDB et transformer
        self.mongo_client = MongoDBClient()
        self.transformer = DataTransformer()
        
        # Cache pour IDs
        self.city_cache = {}
        self.category_cache = {}
    
    def connect(self) -> bool:
        """Connexion à PostgreSQL"""
        try:
            # Fix encodage Windows
            import locale
            locale.setlocale(locale.LC_ALL, 'C')
            
            logger.info("🔌 Connexion à PostgreSQL...")
            logger.info(f"   Host: {self.host}:{self.port}")
            logger.info(f"   Database: {self.database}")
            
            # Utiliser DSN pour éviter problème encodage Windows
            dsn = f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
            
            self.conn = psycopg2.connect(dsn)
            self.cursor = self.conn.cursor()
            
            logger.info("✅ Connexion PostgreSQL établie")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"❌ Erreur connexion PostgreSQL: {e}")
            logger.info("\n💡 Assurez-vous que PostgreSQL est démarré:")
            logger.info("   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres --name postgres postgres:15")
            return False
    
    def initialize_schema(self, schema_file: str = "sql/schema.sql") -> bool:
        """Initialise le schéma SQL"""
        try:
            logger.info(f"📊 Chargement du schéma: {schema_file}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            self.cursor.execute(schema_sql)
            self.conn.commit()
            
            logger.info("✅ Schéma SQL créé")
            return True
            
        except FileNotFoundError:
            logger.error(f"❌ Fichier non trouvé: {schema_file}")
            return False
        except psycopg2.Error as e:
            logger.error(f"❌ Erreur création schéma: {e}")
            self.conn.rollback()
            return False
    
    def get_or_create_city(self, city_name: str) -> int:
        """Récupère ou crée une ville"""
        if not city_name:
            city_name = "Paris"
        
        # Vérifier le cache
        if city_name in self.city_cache:
            return self.city_cache[city_name]
        
        try:
            # Chercher si existe
            self.cursor.execute(
                "SELECT id FROM cities WHERE name = %s",
                (city_name,)
            )
            
            row = self.cursor.fetchone()
            
            if row:
                city_id = row[0]
            else:
                # Créer
                self.cursor.execute(
                    "INSERT INTO cities (name) VALUES (%s) RETURNING id",
                    (city_name,)
                )
                city_id = self.cursor.fetchone()[0]
                self.conn.commit()
            
            self.city_cache[city_name] = city_id
            return city_id
            
        except psycopg2.Error as e:
            logger.error(f"Erreur get_or_create_city: {e}")
            self.conn.rollback()
            return self.get_or_create_city("Paris")  # Fallback
    
    def get_or_create_category(self, category_name: str, parent: Optional[str] = None) -> int:
        """Récupère ou crée une catégorie"""
        if not category_name:
            category_name = "Autre"
        
        cache_key = f"{category_name}_{parent}"
        
        if cache_key in self.category_cache:
            return self.category_cache[cache_key]
        
        try:
            # Chercher si existe
            self.cursor.execute(
                "SELECT id FROM categories WHERE name = %s",
                (category_name,)
            )
            
            row = self.cursor.fetchone()
            
            if row:
                category_id = row[0]
            else:
                # Créer
                self.cursor.execute(
                    "INSERT INTO categories (name, parent_category) VALUES (%s, %s) RETURNING id",
                    (category_name, parent)
                )
                category_id = self.cursor.fetchone()[0]
                self.conn.commit()
            
            self.category_cache[cache_key] = category_id
            return category_id
            
        except psycopg2.Error as e:
            logger.error(f"Erreur get_or_create_category: {e}")
            self.conn.rollback()
            return self.get_or_create_category("Autre")
    
    def insert_event(self, event_data: Dict) -> Optional[int]:
        """Insère un événement"""
        try:
            # Récupérer city_id
            city_id = self.get_or_create_city(event_data.get("city_name"))
            
            # Préparer les données
            sql = """
                INSERT INTO events (
                    raw_id, source, title, description,
                    city_id, address_street, address_name, zipcode, arrondissement,
                    latitude, longitude, distance_center, geocoded,
                    event_date, event_datetime, year, month, day,
                    day_of_week, day_of_week_name, month_name, season, time_period,
                    is_weekend, is_multi_day, duration_days,
                    price_type, price_detail, is_free, accessibility_score,
                    contact_url, contact_phone, contact_email
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s
                )
                ON CONFLICT (raw_id) DO NOTHING
                RETURNING id
            """
            
            values = (
                event_data.get("raw_id"),
                event_data.get("source"),
                event_data.get("title"),
                event_data.get("description"),
                city_id,
                event_data.get("address_street"),
                event_data.get("address_name"),
                event_data.get("zipcode"),
                event_data.get("arrondissement"),
                event_data.get("latitude"),
                event_data.get("longitude"),
                event_data.get("distance_center"),
                event_data.get("geocoded"),
                event_data.get("event_date"),
                event_data.get("event_datetime"),
                event_data.get("year"),
                event_data.get("month"),
                event_data.get("day"),
                event_data.get("day_of_week"),
                event_data.get("day_of_week_name"),
                event_data.get("month_name"),
                event_data.get("season"),
                event_data.get("time_period"),
                event_data.get("is_weekend"),
                event_data.get("is_multi_day"),
                event_data.get("duration_days"),
                event_data.get("price_type"),
                event_data.get("price_detail"),
                event_data.get("is_free"),
                event_data.get("accessibility_score"),
                event_data.get("contact_url"),
                event_data.get("contact_phone"),
                event_data.get("contact_email")
            )
            
            self.cursor.execute(sql, values)
            result = self.cursor.fetchone()
            
            if result:
                event_id = result[0]
                
                # Insérer les catégories
                main_cat = event_data.get("main_category")
                if main_cat:
                    cat_id = self.get_or_create_category(main_cat)
                    self.cursor.execute(
                        """INSERT INTO event_categories (event_id, category_id, is_primary, confidence)
                           VALUES (%s, %s, TRUE, %s)
                           ON CONFLICT DO NOTHING""",
                        (event_id, cat_id, event_data.get("category_confidence", 0.0))
                    )
                
                # Sous-catégorie
                sub_cat = event_data.get("sub_category")
                if sub_cat:
                    cat_id = self.get_or_create_category(sub_cat, parent=main_cat)
                    self.cursor.execute(
                        """INSERT INTO event_categories (event_id, category_id, is_primary, confidence)
                           VALUES (%s, %s, FALSE, %s)
                           ON CONFLICT DO NOTHING""",
                        (event_id, cat_id, event_data.get("category_confidence", 0.0))
                    )
                
                return event_id
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur insertion événement: {e}")
            self.conn.rollback()
            return None
    
    def load_all_events(self) -> Dict:
        """Charge tous les événements depuis MongoDB"""
        stats = {
            "processed": 0,
            "inserted": 0,
            "skipped": 0,
            "errors": 0
        }
        
        if not self.mongo_client.connect():
            logger.error("❌ Impossible de se connecter à MongoDB")
            return stats
        
        try:
            # Récupérer tous les événements enrichis
            enriched_docs = list(self.mongo_client.enriched.find({}))
            total = len(enriched_docs)
            
            logger.info(f"📊 {total} événements enrichis à charger\n")
            
            for i, enriched_doc in enumerate(enriched_docs, 1):
                try:
                    # Récupérer le document RAW
                    raw_id = enriched_doc.get("raw_id")
                    raw_doc = self.mongo_client.raw.find_one({"_id": raw_id})
                    
                    if not raw_doc:
                        stats["errors"] += 1
                        continue
                    
                    # Transformer
                    event_data = self.transformer.transform_event(raw_doc, enriched_doc)
                    
                    if not event_data:
                        stats["errors"] += 1
                        continue
                    
                    # Insérer
                    event_id = self.insert_event(event_data)
                    
                    if event_id:
                        stats["inserted"] += 1
                    else:
                        stats["skipped"] += 1
                    
                    stats["processed"] += 1
                    
                    # Commit tous les 50
                    if i % 50 == 0:
                        self.conn.commit()
                        progress = (i / total) * 100
                        logger.info(f"⏳ Progression: {i}/{total} ({progress:.1f}%)")
                
                except Exception as e:
                    logger.error(f"Erreur événement {i}: {e}")
                    stats["errors"] += 1
            
            # Commit final
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Erreur load_all_events: {e}")
            self.conn.rollback()
        finally:
            self.mongo_client.disconnect()
        
        return stats
    
    def disconnect(self):
        """Fermeture propre"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔌 Connexion PostgreSQL fermée")


def main():
    """🚀 Point d'entrée principal"""
    print("=" * 70)
    print("🗄️ ETL MONGODB → POSTGRESQL")
    print("=" * 70 + "\n")
    
    loader = PostgreSQLLoader()
    
    # Connexion PostgreSQL
    if not loader.connect():
        return
    
    # Initialiser le schéma
    if not loader.initialize_schema():
        loader.disconnect()
        return
    
    # Charger les données
    print("\n💾 Chargement des événements...\n")
    stats = loader.load_all_events()
    
    # Résultats
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS ETL")
    print("=" * 70)
    print(f"\n✅ Traités:  {stats['processed']}")
    print(f"✅ Insérés:  {stats['inserted']}")
    print(f"⏭️ Ignorés:  {stats['skipped']} (doublons)")
    print(f"❌ Erreurs:  {stats['errors']}")
    
    if stats['processed'] > 0:
        success_rate = (stats['inserted'] / stats['processed']) * 100
        print(f"\n📈 Taux de succès: {success_rate:.1f}%")
    
    # Statistiques PostgreSQL
    try:
        loader.cursor.execute("SELECT COUNT(*) FROM events")
        total_events = loader.cursor.fetchone()[0]
        
        loader.cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = loader.cursor.fetchone()[0]
        
        loader.cursor.execute("SELECT COUNT(*) FROM cities")
        total_cities = loader.cursor.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("🗄️ ÉTAT DE LA BASE POSTGRESQL")
        print("=" * 70)
        print(f"\n📄 Événements: {total_events}")
        print(f"🏷️ Catégories: {total_categories}")
        print(f"📍 Villes: {total_cities}")
        
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
    
    loader.disconnect()
    print("\n✅ ETL terminé avec succès!\n")


if __name__ == "__main__":
    main()