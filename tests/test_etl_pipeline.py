import unittest
import json
import sys
from pathlib import Path
from bson import ObjectId

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.transformer import DataTransformer

class TestETLPipeline(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        self.transformer = DataTransformer()
        self.sample_raw_event = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "source": "test",
            "payload": {
                "title": "Concert au Musée",
                "dates": {"start": "2026-03-15"},
                "location": [48.8566, 2.3522],
                "description": "Un concert classique",
                "address": {
                    "street": "10 Rue de Rivoli",
                    "city": "Paris",
                    "zipcode": "75004"
                }
            }
        }
        
        self.sample_enriched_event = {
            "data": {
                "latitude": 48.8566,
                "longitude": 2.3522,
                "geocoded": True,
                "arrondissement": 4,
                "event_date": "2026-03-15"
            }
        }

    def test_transformer_initialization(self):
        """Test transformer initialization"""
        self.assertIsNotNone(self.transformer)
        self.assertEqual(self.transformer.processed_count, 0)
        self.assertEqual(self.transformer.error_count, 0)

    def test_transform_event(self):
        """Test event transformation"""
        transformed = self.transformer.transform_event(self.sample_raw_event, self.sample_enriched_event)
        self.assertIsNotNone(transformed)
        self.assertIn("title", transformed)
        self.assertEqual(transformed["title"], "Concert au Musée")

    def test_load_sample_data(self):
        """Test loading sample events"""
        sample_file = Path(__file__).parent / "sample_events.json"
        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            self.assertIsInstance(events, list)
            if len(events) > 0:
                self.assertIn("title", events[0])

    def test_pipeline_integration(self):
        """Test full pipeline integration"""
        # Transform
        transformed = self.transformer.transform_event(self.sample_raw_event, self.sample_enriched_event)
        self.assertIsNotNone(transformed)
        self.assertEqual(transformed["source"], "test")

if __name__ == '__main__':
    unittest.main()
