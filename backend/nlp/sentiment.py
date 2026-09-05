import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize analyzer globally so it's only done once
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> dict:
    if not text or not text.strip():
        return {"label": "neutral", "confidence": 1.0, "indicators": []}
        
    # Get scores
    scores = sia.polarity_scores(text)
    
    # Determine label from compound score
    # Usually: >= 0.05 is Positive, <= -0.05 is Negative, else Neutral
    compound = scores['compound']
    if compound >= 0.05:
        label = "positive"
        confidence = scores['pos'] / (scores['pos'] + scores['neu'] + scores['neg'] + 1e-9)
        # Ensure confidence looks reasonable, base it slightly on compound
        confidence = max(0.5, abs(compound))
    elif compound <= -0.05:
        label = "negative"
        confidence = max(0.5, abs(compound))
    else:
        label = "neutral"
        # High neutral score usually implies high confidence in it being neutral
        confidence = scores['neu']

    # Extract indicators
    # We tokenize the text and check VADER's lexicon for highly polarized words
    words = text.split()
    indicators_with_scores = []
    
    for w in words:
        # clean punctuation
        clean_w = w.strip(string.punctuation).lower()
        if clean_w in sia.lexicon:
            score = sia.lexicon[clean_w]
            # If the word's polarity matches the overall document polarity
            if (label == "positive" and score > 0) or (label == "negative" and score < 0):
                indicators_with_scores.append((clean_w, abs(score)))
                
    # Sort indicators by highest absolute polarity score
    indicators_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 5 unique indicators
    indicators = []
    seen = set()
    for word, _ in indicators_with_scores:
        if word not in seen:
            seen.add(word)
            indicators.append(word)
            if len(indicators) >= 5:
                break
                
    return {
        "label": label,
        "confidence": round(confidence, 2),
        "indicators": indicators
    }
