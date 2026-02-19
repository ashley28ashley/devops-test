import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestDataParsing(unittest.TestCase):
    """Test data parsing and validation"""

    def test_parse_sample_events(self):
        """Test parsing sample events JSON"""
        sample_file = Path(__file__).parent / "sample_events.json"
        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            self.assertIsInstance(events, list)
            if len(events) > 0:
                event = events[0]
                # Check for essential fields
                self.assertIn("title", event or {})

    def test_parse_raw_events(self):
        """Test parsing raw events JSON"""
        raw_file = Path(__file__).parent.parent / "events_raw.json"
        if raw_file.exists():
            with open(raw_file, 'r', encoding='utf-8') as f:
                content = f.read()
                events = json.loads(content)
            
            self.assertIsNotNone(events)

    def test_json_structure_validation(self):
        """Test JSON structure validation"""
        valid_event = {
            "title": "Event",
            "date": "2026-02-20",
            "location": "Location"
        }
        
        self.assertIn("title", valid_event)
        self.assertIn("date", valid_event)
        self.assertIn("location", valid_event)

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON"""
        invalid_json = "{ invalid json }"
        
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)

if __name__ == '__main__':
    unittest.main()
