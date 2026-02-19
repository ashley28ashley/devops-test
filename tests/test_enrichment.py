import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from enrichment.categorization import CategorizationEnricher
from enrichment.date_processor import DateEnricher
from enrichment.geocoding import GeocodingEnricher

class TestEnrichment(unittest.TestCase):
    """Test data enrichment functions"""

    def setUp(self):
        """Set up test data"""
        self.date_enricher = DateEnricher()
        self.cat_enricher = CategorizationEnricher()
        self.geo_enricher = GeocodingEnricher()
        
        self.sample_event = {
            "payload": {
                "title": "Concert au Musée",
                "dates": {"start": "2026-03-15"},
                "location": [48.8566, 2.3522],
                "description": "Un concert classique"
            }
        }

    def test_date_enricher_exists(self):
        """Test date enricher initialization"""
        self.assertIsNotNone(self.date_enricher)

    def test_categorization_enricher_exists(self):
        """Test categorization enricher initialization"""
        self.assertIsNotNone(self.cat_enricher)

    def test_geocoding_enricher_exists(self):
        """Test geocoding enricher initialization"""
        self.assertIsNotNone(self.geo_enricher)

    def test_enrichment_chain(self):
        """Test complete enrichment chain"""
        event = self.sample_event.copy()
        
        # Process date
        try:
            result = self.date_enricher.enrich(event)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Date enrichment failed: {e}")
        
        # Categorize
        try:
            result = self.cat_enricher.enrich(event)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Categorization failed: {e}")
        
        # Geocode
        try:
            result = self.geo_enricher.enrich(event)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Geocoding failed: {e}")

if __name__ == '__main__':
    unittest.main()
