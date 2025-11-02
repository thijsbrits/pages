import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class GooglePlacesClient:
    """Minimal client for Google Places API (New)."""
    
    BASE_URL = "https://places.googleapis.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY must be provided or set in environment")
    
    def _make_request(self, endpoint: str, payload: dict, field_mask: str) -> dict:
        """Make a request to the Places API."""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }
        
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if "error" in data:
            raise Exception(f"API Error: {data['error']}")
        
        return data
    
    def search_nearby(
        self,
        lat: float,
        lng: float,
        radius: int = 1500,
        included_types: List[str] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """Search for places near a location."""
        payload = {
            "includedTypes": included_types,
            "maxResultCount": max_results,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": radius
                }
            }
        }
        
        fields = [
            "places.id",
            "places.primaryType",
            "places.displayName",
            "places.websiteUri",
            "places.location",
            "places.googleMapsUri",
            "places.businessStatus",
            "places.addressComponents",
        ]
        field_mask = ",".join(fields)
        data = self._make_request("places:searchNearby", payload, field_mask)
        
        return data.get("places", [])


def find_restaurant_urls(
    lat: float = 34.050481,
    lng: float = -118.248526,
    radius: int = 1500

) -> List[Dict[str, str]]:
    """Search for restaurants and return their website URLs."""
    client = GooglePlacesClient()
    places = client.search_nearby(lat, lng, radius, included_types=["restaurant"])
    
    print(f"Found {len(places)} places")
    
    restaurants = []
    for place in places:
        if website := place.get("websiteUri"):
            restaurants.append({
                "name": place.get("displayName", {}).get("text"),
                "website": website,
                "maps_url": place.get("googleMapsUri")
            })
    
    return restaurants