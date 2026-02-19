from pymongo import MongoClient
from datetime import datetime
import re

client = MongoClient("mongodb://localhost:27017/")
db = client["cultural_events"]

raw = db["events_raw"]
enriched = db["events_enriched"]

def detect_season(month):
    if month in [12, 1, 2]:
        return "Hiver"
    if month in [3, 4, 5]:
        return "Printemps"
    if month in [6, 7, 8]:
        return "Été"
    return "Automne"

def is_weekend(date_obj):
    return date_obj.weekday() >= 5

def extract_arrondissement(zipcode):
    if not zipcode or not str(zipcode).startswith("75"):
        return None
    try:
        zipcode_str = str(zipcode)
        num = int(zipcode_str[3:5])
        if 1 <= num <= 20:
            return f"{num}{'er' if num == 1 else 'e'}"
    except:
        pass
    return None

def categorize_event(title, description, category_source):
    """Catégorisation avancée basée sur mots-clés"""
    
    # Concaténer tout le texte
    text = ""
    if title:
        text += title.lower() + " "
    if description:
        text += description.lower() + " "
    if category_source:
        text += str(category_source).lower() + " "
    
    # Dictionnaire de catégories avec mots-clés
    categories = {
        "Musique": {
            "keywords": ["concert", "musique", "musical", "orchestre", "jazz", "rock", "pop", 
                        "classique", "chanson", "rap", "electro", "festival", "scène", "live",
                        "récital", "philharmonique", "symphonie", "opéra", "chanteur", "groupe"],
            "sub": {
                "Jazz": ["jazz", "blues", "swing"],
                "Classique": ["classique", "orchestre", "symphonie", "opéra"],
                "Rock": ["rock", "metal", "punk"],
                "Pop": ["pop", "variété"],
                "Electro": ["electro", "techno", "house", "edm"],
                "Rap/Hip-Hop": ["rap", "hip-hop", "hip hop"],
                "Chanson française": ["chanson française", "variété française"],
            }
        },
        "Théâtre": {
            "keywords": ["théâtre", "theatre", "pièce", "comédie", "tragédie", "spectacle",
                        "mise en scène", "acteur", "troupe", "monologue"],
            "sub": {
                "Comédie": ["comédie", "humour", "rire"],
                "Drame": ["drame", "tragédie"],
            }
        },
        "Danse": {
            "keywords": ["danse", "ballet", "chorégraphie", "chorégraphe", "danseur"],
            "sub": {
                "Ballet": ["ballet"],
                "Hip-Hop": ["hip-hop", "breakdance", "street dance"],
            }
        },
        "Exposition": {
            "keywords": ["exposition", "expo", "musée", "galerie", "art", "peinture", 
                        "sculpture", "photographie", "photo", "vernissage", "œuvre", "artiste"],
            "sub": {
                "Art contemporain": ["contemporain", "moderne"],
                "Peinture": ["peinture", "toile", "tableau"],
                "Sculpture": ["sculpture", "sculpteur"],
                "Photographie": ["photo", "photographie", "photographe"],
            }
        },
        "Cinéma": {
            "keywords": ["cinéma", "cinema", "film", "projection", "séance", "écran",
                        "court-métrage", "long-métrage", "documentaire", "avant-première"],
            "sub": {
                "Avant-première": ["avant-première", "preview"],
                "Festival": ["festival"],
            }
        },
        "Conférence": {
            "keywords": ["conférence", "débat", "table ronde", "rencontre", "discussion",
                        "colloque", "séminaire", "forum"],
            "sub": {}
        },
        "Sport": {
            "keywords": ["sport", "match", "compétition", "tournoi", "championnat",
                        "football", "basket", "tennis", "rugby"],
            "sub": {}
        },
    }
    
    # Compter les correspondances pour chaque catégorie
    scores = {}
    for category, data in categories.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in text:
                score += 1
        if score > 0:
            scores[category] = score
    
    # Déterminer la catégorie principale
    if scores:
        main_category = max(scores, key=scores.get)
        
        # Chercher sous-catégorie
        sub_category = None
        if main_category in categories:
            for sub, keywords in categories[main_category]["sub"].items():
                for keyword in keywords:
                    if keyword in text:
                        sub_category = sub
                        break
                if sub_category:
                    break
        
        return main_category, sub_category
    
    return "Autre", None

def enrich_event(raw_doc):
    payload = raw_doc.get("payload", {})

    title = payload.get("title")
    description = payload.get("description")
    category_source = payload.get("category")

    address = payload.get("address", {})
    zipcode = address.get("zipcode")
    city = address.get("city", "Paris")

    arrondissement = extract_arrondissement(zipcode)

    # Dates
    dates = payload.get("dates", {})
    date_str = dates.get("start") or payload.get("date") or payload.get("event_date")

    if date_str:
        try:
            date_str = str(date_str).replace("Z", "+00:00")
            date_obj = datetime.fromisoformat(date_str)
        except Exception as e:
            date_obj = None
    else:
        date_obj = None

    # Prix
    price = payload.get("price", {})
    price_type = price.get("type", "")
    price_detail = price.get("detail", "")
    is_free = "gratuit" in str(price_type).lower() or "gratuit" in str(price_detail).lower()

    # Catégorisation améliorée
    main_cat, sub_cat = categorize_event(title, description, category_source)

    # Coordonnées GPS
    location = payload.get("location")
    latitude = None
    longitude = None
    if location and isinstance(location, list) and len(location) == 2:
        latitude = location[0]
        longitude = location[1]

    enriched_data = {
        "title": title,
        "description": description,
        "city": city,
        "zipcode": zipcode,
        "arrondissement": arrondissement,

        "event_date": date_obj.date().isoformat() if date_obj else None,
        "event_datetime": date_obj.isoformat() if date_obj else None,
        "year": date_obj.year if date_obj else None,
        "month": date_obj.month if date_obj else None,
        "day": date_obj.day if date_obj else None,
        "day_of_week": (date_obj.weekday() + 1) if date_obj else None,  # 1=Lundi
        "day_of_week_name": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][date_obj.weekday()] if date_obj else None,
        "month_name": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"][date_obj.month - 1] if date_obj else None,
        "season": detect_season(date_obj.month) if date_obj else None,
        "is_weekend": is_weekend(date_obj) if date_obj else False,
        "time_period": None,

        "price_type": str(price_type) if price_type else None,
        "price_detail": str(price_detail) if price_detail else None,
        "is_free": is_free,

        "main_category": main_cat,
        "sub_category": sub_cat,
        "confidence": 0.8,
        "keywords": [],

        "latitude": latitude,
        "longitude": longitude,
        "geocoded": bool(latitude and longitude),
        "distance_center": None,
        "address_quality": "from_source" if latitude else "unknown",
        "accessibility_score": 0.5,
    }

    return {
        "raw_id": raw_doc["_id"],
        "status": "success",
        "enriched_at": datetime.utcnow(),
        "data": enriched_data,
        "error": None
    }

def run_enrichment():
    print("=" * 70)
    print("🎨 ENRICHISSEMENT AMÉLIORÉ")
    print("=" * 70)
    
    # Supprimer les enrichissements existants
    enriched.delete_many({})
    print("🧹 Collection events_enriched vidée\n")

    count = 0
    stats = {}
    
    for raw_doc in raw.find():
        enriched_doc = enrich_event(raw_doc)
        enriched.insert_one(enriched_doc)
        
        # Compter les catégories
        cat = enriched_doc["data"]["main_category"]
        stats[cat] = stats.get(cat, 0) + 1
        
        count += 1
        if count % 50 == 0:
            print(f"⏳ Traité: {count} événements...")

    print(f"\n✅ {count} événements enrichis\n")
    
    print("📊 RÉPARTITION PAR CATÉGORIE:")
    for cat, num in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {num} événements")

if __name__ == "__main__":
    run_enrichment()