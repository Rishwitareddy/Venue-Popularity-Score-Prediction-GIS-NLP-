import requests
import folium
from folium.plugins import MarkerCluster


def generate_cluster_map(place):
    """
    Generates a cluster map for ANY valid city/place.
    NEVER returns None unless the place is totally invalid.
    """

    try:
        # --- Geocoding ---
        geo_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place,
            "format": "json",
            "limit": 1
        }

        response = requests.get(
            geo_url,
            params=params,
            headers={"User-Agent": "EDA-Project"},
            timeout=10
        )

        data = response.json()

        # If geocoding fails, fall back to India center
        if not data:
            lat, lon = 20.5937, 78.9629  # India center
        else:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

        # --- Create map ---
        fmap = folium.Map(location=[lat, lon], zoom_start=12)
        cluster = MarkerCluster().add_to(fmap)

        # Add main marker
        folium.Marker(
            location=[lat, lon],
            popup=f"{place}",
            icon=folium.Icon(color="blue")
        ).add_to(cluster)

        return fmap

    except Exception as e:
        print("Cluster map error:", e)

        # Absolute fallback map (NEVER fails)
        fmap = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        return fmap
