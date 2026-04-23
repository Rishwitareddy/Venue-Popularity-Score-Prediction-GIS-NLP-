import random
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io

class VenueAnalyzer:
    def __init__(self):
        # Expanded adjectives for more variety
        self.positive_adjectives = [
            "amazing", "great", "excellent", "fantastic", "wonderful", 
            "delicious", "superb", "lovely", "brilliant", "outstanding",
            "beautiful", "cozy", "friendly", "clean", "vibrant"
        ]
        self.negative_adjectives = [
            "bad", "terrible", "poor", "awful", "horrible", 
            "disappointing", "mediocre", "rude", "dirty", "slow",
            "noisy", "crowded", "expensive", "tasteless", "stale"
        ]
        self.neutral_adjectives = [
            "average", "okay", "decent", "fine", "standard", 
            "typical", "acceptable", "normal", "basic", "plain"
        ]

    def generate_synthetic_reviews(self, category_name="General", count=5):
        """Generates plausible reviews if real API data is missing."""
        reviews = []
        
        # Simple context based on category
        cat_lower = category_name.lower()
        if "food" in cat_lower or "restaurant" in cat_lower or "cafe" in cat_lower:
            nouns = ["food", "service", "ambiance", "staff", "menu", "coffee", "meal"]
            verbs = ["tasted", "was", "is", "felt"]
        elif "park" in cat_lower or "outdoors" in cat_lower:
            nouns = ["view", "trees", "atmosphere", "path", "benches", "air"]
            verbs = ["looked", "was", "is", "felt"]
        elif "shop" in cat_lower or "store" in cat_lower:
            nouns = ["selection", "price", "staff", "items", "quality", "layout"]
            verbs = ["was", "is", "seemed"]
        else:
            nouns = ["place", "experience", "service", "quality", "vibe"]
            verbs = ["was", "is", "seemed"]

        for _ in range(count):
            sentiment_type = random.choices(["pos", "neg", "neu"], weights=[0.5, 0.2, 0.3])[0]
            
            if sentiment_type == "pos":
                adj = random.choice(self.positive_adjectives)
                text = f"The {random.choice(nouns)} {random.choice(verbs)} {adj}. Definitely recommended!"
            elif sentiment_type == "neg":
                adj = random.choice(self.negative_adjectives)
                text = f"The {random.choice(nouns)} {random.choice(verbs)} {adj}. Not coming back."
            else:
                adj = random.choice(self.neutral_adjectives)
                text = f"The {random.choice(nouns)} {random.choice(verbs)} {adj}. It was alright."
                
            reviews.append(text)
            
        return reviews

    def analyze_sentiment(self, text):
        """Returns polarity (-1 to 1)."""
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def extract_keywords(self, text):
        """Simple keyword extraction using noun phrases."""
        blob = TextBlob(text)
        return list(blob.noun_phrases)

    def calculate_popularity_score(self, reviews):
        """
        Computes a 0-100 score based on sentiment analysis of reviews.
        """
        if not reviews:
            return 50  # Default neutral score
            
        total_sentiment = 0
        for review in reviews:
            total_sentiment += self.analyze_sentiment(review)
            
        avg_sentiment = total_sentiment / len(reviews)
        
        # Normalize -1 to 1 range to 0 to 100
        # -1 -> 0, 0 -> 50, 1 -> 100
        score = (avg_sentiment + 1) * 50
        
        # Add some random variance to simulate realism if identical reviews
        score += random.uniform(-5, 5)
        
        return max(0, min(100, int(score)))

    def generate_wordcloud(self, text, output_path):
        """Generates and saves a wordcloud image."""
        if not text.strip():
            return None
            
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        wc.to_file(output_path)
        return output_path

    def generate_sentiment_graph(self, scores, output_path):
        """Generates a bar chart of sentiment distribution."""
        labels = ['Positive', 'Neutral', 'Negative']
        
        # Categorize scores
        pos = sum(1 for s in scores if s > 60)
        neu = sum(1 for s in scores if 40 <= s <= 60)
        neg = sum(1 for s in scores if s < 40)
        
        values = [pos, neu, neg]
        colors = ['green', 'gray', 'red']

        plt.figure(figsize=(6, 4))
        plt.bar(labels, values, color=colors)
        plt.title('Sentiment Distribution of Venues')
        plt.xlabel('Sentiment Class')
        plt.ylabel('Number of Venues')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return output_path
