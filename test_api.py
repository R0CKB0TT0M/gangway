import json
import unittest
from unittest.mock import MagicMock, patch

from main import app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_animations(self):
        response = self.client.get("/animations")
        self.assertEqual(response.status_code, 200)
        animations = json.loads(response.data)
        self.assertIsInstance(animations, list)
        self.assertGreater(len(animations), 0)
        for animation in animations:
            self.assertIn("name", animation)
            self.assertIn("module", animation)
            self.assertIn("params", animation)

    def test_get_animation_schema(self):
        response = self.client.get("/animations")
        animations = json.loads(response.data)
        for animation in animations:
            response = self.client.get(f"/animations/{animation['name']}/schema")
            self.assertEqual(response.status_code, 200)
            schema = json.loads(response.data)
            self.assertIn("title", schema)
            self.assertIn("type", schema)
            self.assertIn("properties", schema)

            self.assertIn("properties", schema)

if __name__ == "__main__":
    unittest.main()
