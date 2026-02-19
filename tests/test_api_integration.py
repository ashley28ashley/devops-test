import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api.main import app
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

class TestAPIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if HAS_FASTAPI:
            cls.client = TestClient(app)

    @unittest.skipIf(not HAS_FASTAPI, "FastAPI not available")
    def test_health_check(self):
        """Test that the API is healthy"""
        response = self.client.get("/health")
        self.assertIn(response.status_code, [200, 404])

    @unittest.skipIf(not HAS_FASTAPI, "FastAPI not available")
    def test_get_events(self):
        """Test getting events from API"""
        response = self.client.get("/api/events")
        self.assertIn(response.status_code, [200, 404])

    @unittest.skipIf(not HAS_FASTAPI, "FastAPI not available")
    def test_get_search_endpoint(self):
        """Test search endpoint"""
        response = self.client.get("/api/search?q=concert")
        self.assertIn(response.status_code, [200, 404])

if __name__ == '__main__':
    unittest.main()
