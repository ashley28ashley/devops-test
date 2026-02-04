import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


class CategorizationEnricher:
    """Catégorisation automatique basée sur mots-clés et règles"""
    
    def __init__(self):
        # Dictionnaire de catégorisation
        self.categories = {
            "Musique": {
                "keywords": ["concert", "musique", "musical", "orchestre", "jazz", "rock", "pop", "classique", "chanson", "rap", "electro", "festival", "scène", "live"],
                "subcategories": {
                    "Jazz": ["jazz", "blues", "swing"],
                    "Classique": ["classique", "orchestre", "symphonie", "opéra", "philharmonique"],
                    "Rock": ["rock", "metal", "punk"],
                    "Pop": ["pop", "variété"],
                    "Electro": ["electro", "techno", "house", "edm"],
                    "Rap/Hip-Hop": ["rap", "hip-hop", "hip hop"],
                    "Chanson française": ["chanson", "variété française"],
                    "World": ["world", "afro", "latino", "reggae"]
                }
            },
            "Théâtre": {
                "keywords": ["théâtre", "pièce", "comédie", "tragédie", "spectacle", "mise en scène", "acteur", "scène"],
                "subcategories": {
                    "Comédie": ["comédie", "humour", "rire"],
                    "Drame": ["drame", "tragédie"],
                    "Contemporain": ["contemporain", "moderne"],
                    "Classique": ["molière", "shakespeare", "racine"]
                }
            },
            "Danse": {
                "keywords": ["danse", "ballet", "chorégraphie", "hip-hop dance", "contemporain"],
                "subcategories": {
                    "Ballet": ["ballet", "classique"],
                    "Contemporain": ["contemporain", "moderne"],
                    "Hip-Hop": ["hip-hop", "breakdance", "street"],
                    "Traditionnel": ["folklore", "traditionnel"]
                }
            },
            "Exposition": {
                "keywords": ["exposition", "expo", "musée", "galerie", "art", "peinture", "sculpture", "photographie", "vernissage"],
                "subcategories": {
                    "Art contemporain": ["contemporain", "moderne"],
                    "Peinture": ["peinture", "toile"],
                    "Sculpture": ["sculpture"],
                    "Photographie": ["photo", "photographie"],
                    "Art classique": ["classique", "impressionnisme"]
                }
            },
            "Cinéma": {
                "keywords": ["cinéma", "film", "projection", "séance", "festival du film"],
                "subcategories": {
                    "Avant-première": ["avant-première", "preview"],
                    "Festival": ["festival"],
                    "Cinéma d'art": ["art et essai", "auteur"]
                }
            },
            "Conférence": {
                "keywords": ["conférence", "débat", "table ronde", "rencontre", "discussion"],
                "subcategories": {
                    "Scientifique": ["science", "recherche"],
                    "Littéraire": ["littérature", "livre"],
                    "Débat": ["débat", "discussion"]
                }
            },
            "Sport": {
                "keywords": ["sport", "match", "compétition", "tournoi", "championnat"],
                "subcategories": {
                    "Football": ["football", "foot"],
                    "Basketball": ["basket"],
                    "Tennis": ["tennis"],
                    "Autre": ["sport"]
                }
            },
            "Festival": {
                "keywords": ["festival"],
                "subcategories": {}
            },
            "Autre": {
                "keywords": [],
                "subcategories": {}
            }
        }
    
    def enrich(self, event: Dict) -> Dict:
        """Enrichit un événement avec catégorisation"""
        result = {
            "main_category": "Autre",
            "sub_category": None,
            "keywords": [],
            "confidence": 0.0
        }
        
        try:
            payload = event.get("payload", {})
            
            # Extraire le texte à analyser (avec gestion de None)
            title = (payload.get("title") or "").lower()
            description = (payload.get("description") or "").lower()
            category_source = (payload.get("category") or "").lower()
            tags = payload.get("tags", [])
            
            # Concaténer tout le texte
            full_text = f"{title} {description} {category_source}"
            if isinstance(tags, list):
                full_text += " " + " ".join(str(t).lower() for t in tags)
            
            # Chercher les catégories
            scores = {}
            
            for category, data in self.categories.items():
                score = 0
                matched_keywords = []
                
                # Compter les mots-clés trouvés
                for keyword in data["keywords"]:
                    if keyword in full_text:
                        score += 1
                        matched_keywords.append(keyword)
                
                if score > 0:
                    scores[category] = {
                        "score": score,
                        "keywords": matched_keywords
                    }
            
            # Déterminer la catégorie principale
            if scores:
                best_category = max(scores.items(), key=lambda x: x[1]["score"])
                result["main_category"] = best_category[0]
                result["keywords"] = best_category[1]["keywords"]
                result["confidence"] = min(best_category[1]["score"] / 3.0, 1.0)
                
                # Chercher la sous-catégorie
                subcats = self.categories[best_category[0]]["subcategories"]
                for subcat, subcat_keywords in subcats.items():
                    for keyword in subcat_keywords:
                        if keyword in full_text:
                            result["sub_category"] = subcat
                            break
                    if result["sub_category"]:
                        break
            
            # Utiliser la catégorie source si disponible
            if category_source and result["confidence"] < 0.5:
                mapped_category = self._map_source_category(category_source)
                if mapped_category:
                    result["main_category"] = mapped_category
                    result["confidence"] = 0.6
            
        except Exception as e:
            logger.error(f"Erreur catégorisation: {e}")
        
        return result
    
    def _map_source_category(self, source_category: str) -> str:
        """Mappe les catégories sources vers nos catégories"""
        mapping = {
            "concert": "Musique",
            "musique": "Musique",
            "spectacle": "Théâtre",
            "theatre": "Théâtre",
            "exposition": "Exposition",
            "expo": "Exposition",
            "cinema": "Cinéma",
            "danse": "Danse",
            "conference": "Conférence",
            "sport": "Sport",
            "festival": "Festival"
        }
        
        source_lower = source_category.lower()
        for key, value in mapping.items():
            if key in source_lower:
                return value
        
        return None
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrait les mots-clés importants d'un texte"""
        # Mots vides à ignorer
        stop_words = {
            "le", "la", "les", "un", "une", "des", "et", "ou", "mais", "donc",
            "de", "du", "à", "au", "aux", "pour", "par", "sur", "dans", "avec",
            "est", "sont", "a", "ont", "sera", "seront", "être", "avoir"
        }
        
        # Extraire les mots
        words = re.findall(r'\b\w{4,}\b', text.lower())
        
        # Filtrer et compter
        word_count = {}
        for word in words:
            if word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1
        
        # Trier par fréquence
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, count in sorted_words[:max_keywords]]


if __name__ == "__main__":
    print("🧪 TEST CATÉGORISATION\n")
    
    enricher = CategorizationEnricher()
    
    # Test 1 : Concert de jazz
    event1 = {
        "payload": {
            "title": "Concert de Jazz exceptionnel",
            "description": "Venez découvrir un spectacle de jazz unique avec des artistes internationaux",
            "category": "Musique"
        }
    }
    
    result1 = enricher.enrich(event1)
    print("Test 1 : Concert de Jazz")
    print(f"✅ Catégorie: {result1['main_category']}")
    print(f"✅ Sous-catégorie: {result1['sub_category']}")
    print(f"✅ Mots-clés: {result1['keywords']}")
    print(f"✅ Confiance: {result1['confidence']:.2f}\n")
    
    # Test 2 : Exposition
    event2 = {
        "payload": {
            "title": "Exposition de peinture contemporaine",
            "description": "Galerie d'art moderne avec vernissage",
            "category": "Exposition"
        }
    }
    
    result2 = enricher.enrich(event2)
    print("Test 2 : Exposition")
    print(f"✅ Catégorie: {result2['main_category']}")
    print(f"✅ Sous-catégorie: {result2['sub_category']}")
    print(f"✅ Mots-clés: {result2['keywords']}")
    print(f"✅ Confiance: {result2['confidence']:.2f}\n")
    
    print("✅ Tests terminés")