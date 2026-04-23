import requests
import folium
import os
from NLP_Analysis import VenueAnalyzer

FOURSQUARE_API_KEY = "fsq3bXxtcgaCBMB1ksK2VmzjGaqA1hPti2y8UO+eSwyyUJw="

def EDA(place, category_id, category_name):
    # Initialize NLP Analyzer
    analyzer = VenueAnalyzer()
    
    # Storage for aggregate analysis
    all_reviews_text = ""
    all_scores = []

    # ---------- GEOCODING ----------
    # First, get the coordinates of the city/place
    geo_url = "https://nominatim.openstreetmap.org/search"
    geo_params = {"q": place, "format": "json", "limit": 1}

    try:
        geo_res = requests.get(
            geo_url,
            params=geo_params,
            headers={"User-Agent": "EDA-Project"},
            timeout=10
        )
        geo_data = geo_res.json()
    except Exception as e:
        print(f"Geocoding Error: {e}")
        geo_data = []

    if not geo_data:
        lat, lon = 20.5937, 78.9629 # Default fallback (India Center)
        print("Geocoding failed, using default location.")
    else:
        lat = float(geo_data[0]["lat"])
        lon = float(geo_data[0]["lon"])

    fmap = folium.Map(location=[lat, lon], zoom_start=12)

    # ---------- DATA FETCHING (FSQ V3 with OSM Fallback) ----------
    venues = []
    
    # Try Foursquare V3 First
    fsq_url = "https://api.foursquare.com/v3/places/search"
    fsq_headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    fsq_params = {
        "ll": f"{lat},{lon}",
        "categories": category_id,
        "radius": 10000, # 10km radius
        "limit": 50
    }

    try:
        print("Attempting Foursquare API...")
        response = requests.get(fsq_url, headers=fsq_headers, params=fsq_params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            venues = data.get("results", [])
            print(f"Foursquare found {len(venues)} venues.")
        else:
            print(f"Foursquare API Error: {response.status_code} {response.text}")
            # If 410 or other error, venues remains empty, triggering fallback
    except Exception as e:
        print(f"Foursquare Exception: {e}")

    # Fallback to Nominatim (OpenStreetMap) if Foursquare failed or returned nothing
    if not venues:
        print("Falling back to OpenStreetMap (Nominatim)...")
        osm_url = "https://nominatim.openstreetmap.org/search"
        import random
        
        # Progressive Query Broadening
        queries_to_try = [
            f"{category_name} in {place}",
            f"{category_name.split()[0]} in {place}",
            f"Restaurant in {place}",
            f"Food in {place}",
            f"Point of Interest in {place}"
        ]
        
        for query in queries_to_try:
            print(f"Trying OSM query: '{query}'")
            osm_params = {
                "q": query,
                "format": "json",
                "limit": 50,
                "addressdetails": 1
            }
            
            try:
                osm_res = requests.get(
                    osm_url, 
                    params=osm_params, 
                    headers={"User-Agent": "EDA-Project"},
                    timeout=15
                )
                if osm_res.status_code == 200:
                    osm_venues = osm_res.json()
                    print(f"OSM found {len(osm_venues)} venues for query '{query}'.")
                    
                    if len(osm_venues) >= 5:
                        # Normalize OSM data to match Foursquare structure for easier processing
                        for v in osm_venues:
                            # Add a tiny random jitter to coordinates so overlapping markers don't perfectly hide each other
                            lat_jitter = random.uniform(-0.0005, 0.0005)
                            lon_jitter = random.uniform(-0.0005, 0.0005)
                            
                            venues.append({
                                "name": v.get("display_name", "").split(",")[0],
                                "lines": [], # OSM doesn't give discrete address lines easily
                                "location": {
                                    "formatted_address": [v.get("display_name", "")]
                                },
                                "geocodes": {
                                    "main": {
                                        "latitude": float(v.get("lat")) + lat_jitter,
                                        "longitude": float(v.get("lon")) + lon_jitter
                                    }
                                },
                                "categories": [{"name": category_name}] 
                            })
                        break # Stop trying broader queries if we got enough results
            except Exception as e:
                print(f"OSM Fallback Error: {e}")

    # ---------- MARKER RENDERING & NLP ----------
    if not venues:
        folium.Marker(
            location=[lat, lon],
            popup=f"No venues found for '{category_name}' in {place} (checked FSQ & OSM)",
            icon=folium.Icon(color="darkred", icon="remove")
        ).add_to(fmap)
        return fmap, {}

    # Create assets directory if not exists
    if not os.path.exists("assets"):
        os.makedirs("assets")

    for venue in venues:
        name = venue.get("name", "Unknown")
        
        # safely get coordinates
        geo = venue.get("geocodes", {}).get("main")
        if not geo: 
            # Foursquare sometimes puts it at top level if from different endpoint, 
            # but we standardized OSM to match. Double check structure.
            continue
            
        latitude = geo.get("latitude")
        longitude = geo.get("longitude")
        
        location = venue.get("location", {})
        address_list = location.get("formatted_address", [])
        address = ", ".join(address_list) if isinstance(address_list, list) else str(address_list)
        
        if not address:
             address = "Address not available"

        # Determine category name for better synthetic reviews
        venue_cats = venue.get("categories", [])
        cat_name = venue_cats[0]["name"] if venue_cats else category_name

        # --- NLP PROCESSING ---
        # 1. Generate Synthetic Reviews (Since APIs don't give full reviews on free tier)
        reviews = analyzer.generate_synthetic_reviews(category_name=cat_name, count=5)
        
        # 2. Analyze
        pop_score = analyzer.calculate_popularity_score(reviews)
        sentiment_label = "Positive" if pop_score >= 60 else "Negative" if pop_score < 40 else "Neutral"
        
        # 3. Aggregate for dashboard
        all_reviews_text += " ".join(reviews) + " "
        all_scores.append(pop_score)

        # 4. Color Coding
        if pop_score >= 75:
            color = "green"
        elif pop_score >= 40:
            color = "orange"
        else:
            color = "red"

        # 5. Popup Content (HTML)
        popup_html = f"""
        <div style="font-family: Arial; width: 250px;">
            <h4 style="margin-bottom: 5px; color: #333;">{name}</h4>
            <span style="color: #666; font-size: 12px;">{cat_name}</span><br>
            <hr style="margin: 5px 0;">
            <b>Popularity Score:</b> <span style="font-size: 14px; text-shadow: 0 0 1px;">{pop_score}/100</span><br>
            <b>Sentiment:</b> {sentiment_label}<br>
            <br>
            <i style="font-size: 11px;">{address[:100]}...</i>
        </div>
        """

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(fmap)

    # --- GENERATE AGGREGATE VISUALS ---
    visuals = {}
    if all_reviews_text:
        wc_path = os.path.abspath("assets/wordcloud.png")
        analyzer.generate_wordcloud(all_reviews_text, wc_path)
        visuals["wordcloud"] = wc_path
        
    if all_scores:
        graph_path = os.path.abspath("assets/sentiment_graph.png")
        analyzer.generate_sentiment_graph(all_scores, graph_path)
        visuals["graph"] = graph_path

    return fmap, visuals
