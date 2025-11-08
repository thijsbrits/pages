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
    
    def _make_request(self, endpoint: str, payload: dict, field_mask: str, is_get: bool = False) -> dict:
        """Make a request to the Places API."""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }
        
        url = f"{self.BASE_URL}/{endpoint}"
        if is_get:
            response = requests.get(url, params=payload, headers=headers)
        else:
            response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if "error" in data:
            raise Exception(f"API Error: {data['error']}")
        
        return data

    def get_place_photos(self, place_id: str) -> Dict:
        """Get details for a place."""

        field_mask = "id,displayName,photos"
        data = self._make_request(f"places/{place_id}", payload=None, field_mask=field_mask, is_get=True)
        return data

    def get_place_photo(self, name: str, max_height: int = 400, max_width: int = 400) -> Dict:
        """Get a photo for a place."""
        
        data = requests.get(f"{self.BASE_URL}/{name}/media?maxHeightPx={max_height}&maxWidthPx={max_width}&key={self.api_key}")
        return data.content
    
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

if __name__ == "__main__":
    import json
    client = GooglePlacesClient()
    # places = client.search_nearby(34.050481, -118.248526, radius=1500, included_types=["restaurant"])
    
    # data = client.get_place_photos("ChIJqbKnF0vGwoARREUrVhYGqTU")
    # print(json.dumps(data, indent=4))

    data = client.get_place_photo("places/ChIJqbKnF0vGwoARREUrVhYGqTU/photos/AWn5SU4xsvpw2WxB12fgP3S9VEoXKe8W7-JSLrCrxCYrlwgUn5QEIuJl9gUN3RlgXIox5Trqg-NRPhv_1klF2Ni3Y050N_NfyirdEdQd3f25GwMr_ffh875W12d2D7zVor5T_pWfJ2c_-AuYKoXBtr3mtN-Ic4q48ZTAaq6XPAawJHXtRa1sYZ3HaNjK2tkOwRs8MJ07Q954ZOCVekoH9vbN5kCqA-GUUIiHbecZCAbHlCpa_ITbrLSV-jUC3z3xARkgOZrMRP_IXlZfHqXHsf8YvN4O5esPV-F4Ay4xbCAQD4ib6DLvrm2pHBGZcKtiBUIUeHx9B8vhr7kOJoD4fiuTFlZK5hqkMaNLIK_nNPNacw2e2geY2FalnwV6fpMHBxHZiy41uWdXqLl-J35Vq1xFutHSLhqPcIQJXCt-71bVK1PbiUvI")
    print(data)