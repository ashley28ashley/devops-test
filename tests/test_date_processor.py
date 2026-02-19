import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from enrichment.date_processor import DateEnricher

class TestDateProcessor(unittest.TestCase):
    def setUp(self):
        self.enricher = DateEnricher()
    
    def test_date_enricher_exists(self):
        self.assertIsNotNone(self.enricher)
    
    def test_date_enricher_has_enrich_method(self):
        self.assertTrue(hasattr(self.enricher, 'enrich'))

if __name__ == '__main__':
    unittest.main()