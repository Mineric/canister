import unittest
from unittest.mock import patch
from web_search import WebSearch

class TestWebSearchIntegration(unittest.TestCase):
    @patch('web_search.requests.get')
    def test_web_search(self, mock_get):
        """Test the web search integration with mock data."""
        # Define mock response data
        mock_response_data = {
            "items": [
                {"title": "Top Programming Tools 2023", "link": "http://example.com/tools"}
            ]
        }
        
        # Configure the mock to return a response with the JSON data
        mock_get.return_value.json.return_value = mock_response_data
        mock_get.return_value.raise_for_status = lambda: None
        
        api_key = "YOUR_API_KEY"
        search_engine_id = "YOUR_SEARCH_ENGINE_ID"
        
        searcher = WebSearch(api_key=api_key, search_engine_id=search_engine_id)
        
        # Performing a mock search
        results = searcher.search("latest programming tools 2023")
        self.assertIsNotNone(results, "No results returned from the web search.")
        self.assertGreater(len(results), 0, "Empty results returned from the web search.")
        print("Mock test passed: Successfully simulated a web search.")

if __name__ == '__main__':
    unittest.main()
