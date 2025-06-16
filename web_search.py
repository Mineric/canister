import requests
import logging

class WebSearch:
    def __init__(self, api_key, search_engine_id=None):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.service_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query):
        """Performs a web search using Google Custom Search API."""
        try:
            parameters = {
                "q": query,
                "key": self.api_key,
                "cx": self.search_engine_id
            }
            response = requests.get(self.service_url, params=parameters)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP error occurred: {err}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

# Sample usage (this should be in your main or test logic with valid API key & CX):
# searcher = WebSearch(api_key="YOUR_API_KEY", search_engine_id="YOUR_SEARCH_ENGINE_ID")
# results = searcher.search("latest programming tools 2023")
# for result in results:
#     print(result.get("title"), result.get("link"))