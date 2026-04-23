import requests

API_KEY = "fsq3bXxtcgaCBMB1ksK2VmzjGaqA1hPti2y8UO+eSwyyUJw="

url = "https://api.foursquare.com/v3/places/search"
headers = {
    "Accept": "application/json",
    "Authorization": API_KEY
}
params = {
    "ll": "19.0760,72.8777", # Mumbai
    "query": "Indian Restaurant",
    "limit": 1
}

print(f"Testing Key: {API_KEY}")
response = requests.get(url, headers=headers, params=params)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
