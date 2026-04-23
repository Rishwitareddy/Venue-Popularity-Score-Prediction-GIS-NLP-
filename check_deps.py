import sys
import pkg_resources
import importlib

required = {'folium', 'requests', 'textblob', 'wordcloud', 'matplotlib', 'Pillow'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print(f"Missing packages: {missing}")
else:
    print("All python packages installed.")

try:
    import textblob
    from textblob import TextBlob
    blob = TextBlob("test")
    print(blob.sentiment)
    print("TextBlob functional.")
except Exception as e:
    print(f"TextBlob error: {e}")
