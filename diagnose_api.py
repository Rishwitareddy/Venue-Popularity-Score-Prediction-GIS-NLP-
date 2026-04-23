import requests

API_KEY = "fsq3bXxtcgaCBMB1ksK2VmzjGaqA1hPti2y8UO+eSwyyUJw="

endpoints = [
    "https://api.foursquare.com/v3/places/search",
    "https://api.foursquare.com/v2/venues/search" # Legacy check
]

headers_v3 = {
    "Accept": "application/json",
    "Authorization": API_KEY
}

headers_v3_bearer = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

params = {
    "ll": "19.0760,72.8777",
    "query": "food",
    "limit": 1
}

print(f"--- Diagnosing Key: {API_KEY[:10]}... ---")

# Test 1: Standard V3
print("\nTest 1: Standard V3")
try:
    r = requests.get(endpoints[0], headers=headers_v3, params=params)
    print(f"URL: {r.url}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: V3 with Bearer (Just in case)
print("\nTest 2: V3 with Bearer")
try:
    r = requests.get(endpoints[0], headers=headers_v3_bearer, params=params)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Legacy V2 (requires date)
print("\nTest 3: Legacy V2 URL (with V3 Key? Unlikely to work but checking 410)")
params_v2 = params.copy()
params_v2['v'] = '20231010'
# params_v2['client_id'] = '...' # we don't have one, just checking if key works as token?
try:
    r = requests.get(endpoints[1], params=params_v2, headers=headers_v3)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
