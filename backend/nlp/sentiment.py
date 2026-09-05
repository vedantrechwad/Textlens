import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize VADER globally
sia = SentimentIntensityAnalyzer()

# Lazy load Hugging Face transformer
hf_pipeline = None

def get_hf_pipeline():
    global hf_pipeline
    if hf_pipeline is None:
        from transformers import pipeline
        # Use a model that predicts POSITIVE / NEGATIVE
        hf_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    return hf_pipeline

def analyze_sentiment(text: str, model_type: str = "vader") -> dict:
    if not text or not text.strip():
        return {"label": "neutral", "confidence": 1.0, "indicators": []}
        
    if model_type == "transformer":
        try:
            pipe = get_hf_pipeline()
            # Distilbert has max length of 512 tokens. We'll just truncate text for safety.
            truncated_text = text[:1500] 
            result = pipe(truncated_text)[0]
            label = result['label'].lower() # 'positive' or 'negative'
            confidence = result['score']
            
            # Since SST-2 doesn't do Neutral natively, we can manually enforce it 
            # if confidence is extremely low for either, but SST-2 is binary and usually highly confident.
            # We'll just pass the binary label.
            
            # We don't have easy word-level indicators from a basic pipeline without interpretability tools
            # So we fallback to VADER's lexicon just to pick out the highlighted words for the UI
            indicators = []
            words = text.split()
            indicators_with_scores = []
            for w in words:
                clean_w = w.strip(string.punctuation).lower()
                if clean_w in sia.lexicon:
                    score = sia.lexicon[clean_w]
                    if (label == "positive" and score > 0) or (label == "negative" and score < 0):
                        indicators_with_scores.append((clean_w, abs(score)))
            indicators_with_scores.sort(key=lambda x: x[1], reverse=True)
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
        except Exception as e:
            return {"label": "neutral", "confidence": 0, "indicators": [f"ERROR: {str(e)}"]}
            
    # VADER Execution
    scores = sia.polarity_scores(text)
    
    # Usually: >= 0.05 is Positive, <= -0.05 is Negative, else Neutral
    compound = scores['compound']
    if compound >= 0.05:
        label = "positive"
        confidence = scores['pos'] / (scores['pos'] + scores['neu'] + scores['neg'] + 1e-9)
        confidence = max(0.5, abs(compound))
    elif compound <= -0.05:
        label = "negative"
        confidence = max(0.5, abs(compound))
    else:
        label = "neutral"
        confidence = scores['neu']

    words = text.split()
    indicators_with_scores = []
    
    for w in words:
        clean_w = w.strip(string.punctuation).lower()
        if clean_w in sia.lexicon:
            score = sia.lexicon[clean_w]
            if (label == "positive" and score > 0) or (label == "negative" and score < 0):
                indicators_with_scores.append((clean_w, abs(score)))
                
    indicators_with_scores.sort(key=lambda x: x[1], reverse=True)
    
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
