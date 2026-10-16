import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from backend.nlp.entity_peek import (
    get_entity_summary,
    extract_first_sentence,
    _CACHE
)
from backend.app import app


class TestEntityPeek(unittest.TestCase):

    def setUp(self):
        # Clear cache before each test
        _CACHE.clear()
        self.client = app.test_client()

    def test_first_sentence_extraction_standard(self):
        extract = "Ada Lovelace was an English mathematician and writer. She is chiefly known for her work on the Analytical Engine."
        result = extract_first_sentence(extract)
        self.assertEqual(result, "Ada Lovelace was an English mathematician and writer.")

    def test_first_sentence_extraction_abbreviation_guard(self):
        # A sentence where first sentence token is under 20 characters due to an abbreviation
        extract = "Dr. Jane is a renowned scientist who pioneered genetic sequencing across multiple universities worldwide."
        result = extract_first_sentence(extract)
        # Should not just be "Dr." (under 20 chars); it guards and preserves context
        self.assertTrue(len(result) >= 20)
        self.assertIn("Jane is a renowned scientist", result)

    def test_first_sentence_extraction_empty(self):
        self.assertEqual(extract_first_sentence(""), "")
        self.assertEqual(extract_first_sentence("   "), "")

    @patch('backend.nlp.entity_peek.requests.get')
    def test_entity_peek_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "standard",
            "title": "Ada Lovelace",
            "description": "English mathematician and writer",
            "extract": "Ada Lovelace was an English mathematician and writer. She worked on Charles Babbage's mechanical computer.",
            "thumbnail": {"source": "https://example.com/ada.jpg"},
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Ada_Lovelace"}}
        }
        mock_get.return_value = mock_response

        res = get_entity_summary("Ada Lovelace", "PERSON")
        self.assertTrue(res["found"])
        self.assertEqual(res["title"], "Ada Lovelace")
        self.assertEqual(res["description"], "English mathematician and writer")
        self.assertEqual(res["fact"], "Ada Lovelace was an English mathematician and writer.")
        self.assertEqual(res["thumbnail"], "https://example.com/ada.jpg")
        self.assertEqual(res["url"], "https://en.wikipedia.org/wiki/Ada_Lovelace")

    @patch('backend.nlp.entity_peek.requests.get')
    def test_entity_peek_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        res = get_entity_summary("NonExistentEntityXYZ12345", "ORG")
        self.assertFalse(res["found"])

    @patch('backend.nlp.entity_peek.requests.get')
    def test_entity_peek_disambiguation_resolved(self, mock_get):
        # 1. Summary call -> disambiguation
        disambig_response = MagicMock()
        disambig_response.status_code = 200
        disambig_response.json.return_value = {
            "type": "disambiguation",
            "title": "Apple"
        }

        # 2. Search call -> finds Apple Inc.
        search_response = MagicMock()
        search_response.status_code = 200
        search_response.json.return_value = {
            "pages": [{"key": "Apple_Inc.", "title": "Apple Inc."}]
        }

        # 3. Second summary call -> standard page
        resolved_response = MagicMock()
        resolved_response.status_code = 200
        resolved_response.json.return_value = {
            "type": "standard",
            "title": "Apple Inc.",
            "description": "American multinational technology company",
            "extract": "Apple Inc. is an American multinational corporation and technology company. It is famous for the iPhone.",
            "thumbnail": {"source": "https://example.com/apple.jpg"},
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Apple_Inc."}}
        }

        mock_get.side_effect = [disambig_response, search_response, resolved_response]

        res = get_entity_summary("Apple", "ORG")
        self.assertTrue(res["found"])
        self.assertEqual(res["title"], "Apple Inc.")
        self.assertIn("Apple Inc. is an American multinational corporation", res["fact"])

    @patch('backend.nlp.entity_peek.requests.get')
    def test_entity_peek_disambiguation_unresolved(self, mock_get):
        disambig_response = MagicMock()
        disambig_response.status_code = 200
        disambig_response.json.return_value = {
            "type": "disambiguation",
            "title": "Mercury"
        }

        search_response = MagicMock()
        search_response.status_code = 200
        search_response.json.return_value = {"pages": []}

        mock_get.side_effect = [disambig_response, search_response]

        res = get_entity_summary("Mercury", "PRODUCT")
        self.assertFalse(res["found"])
        self.assertEqual(res.get("reason"), "ambiguous")

    @patch('backend.nlp.entity_peek.requests.get')
    def test_entity_peek_timeout(self, mock_get):
        mock_get.side_effect = requests.Timeout("Connection timed out")
        res = get_entity_summary("TimeoutCity", "GPE")
        self.assertFalse(res["found"])

    @patch('backend.nlp.entity_peek.requests.get')
    def test_api_route_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "standard",
            "title": "Mumbai",
            "description": "Capital city of Maharashtra, India",
            "extract": "Mumbai is the financial capital of India.",
            "thumbnail": None,
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Mumbai"}}
        }
        mock_get.return_value = mock_response

        response = self.client.get('/api/entity-peek?name=Mumbai&label=GPE')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue(json_data["found"])
        self.assertEqual(json_data["title"], "Mumbai")

    def test_api_route_validation(self):
        # Missing name
        r1 = self.client.get('/api/entity-peek')
        self.assertEqual(r1.status_code, 400)

        # Name exceeds 100 characters
        long_name = "A" * 101
        r2 = self.client.get(f'/api/entity-peek?name={long_name}')
        self.assertEqual(r2.status_code, 400)

        # Invalid label
        r3 = self.client.get('/api/entity-peek?name=London&label=INVALID_LABEL')
        self.assertEqual(r3.status_code, 400)


if __name__ == '__main__':
    unittest.main()
