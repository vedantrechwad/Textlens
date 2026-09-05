import os
import pickle
from backend.config import Config
from backend.nlp.preprocessing import preprocess_for_sentiment
import warnings

# Suppress warnings from scikit-learn
warnings.filterwarnings("ignore", category=UserWarning)

model = None
vectorizer = None

def load_models():
    global model, vectorizer
    if model is None or vectorizer is None:
        try:
            with open(Config.SENTIMENT_MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            with open(Config.TFIDF_VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
        except Exception as e:
            print(f"Error loading sentiment models: {e}")
            model = None
            vectorizer = None

def analyze_sentiment(text: str) -> dict:
    load_models()
    if model is None or vectorizer is None:
        return {"error": "Sentiment models not loaded."}
        
    processed_text = preprocess_for_sentiment(text)
    if not processed_text:
        return {"label": "neutral", "confidence": 1.0, "indicators": []}
        
    # Transform
    vec = vectorizer.transform([processed_text])
    
    # Predict
    pred = model.predict(vec)[0]
    
    # Get confidence if model supports predict_proba, else default to something based on decision function
    confidence = 0.85 # default fallback
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(vec)[0]
        confidence = float(max(proba))
    elif hasattr(model, 'decision_function'):
        df = model.decision_function(vec)[0]
        # map distance from hyperplane to roughly 0.5-1.0
        confidence = 0.5 + 0.5 * (abs(df) / (abs(df) + 1.0))
        
    label = "positive" if pred == 1 else "negative"
    
    # Extract indicators (features that drove the prediction)
    # We look at the words in the text that have the highest TF-IDF weight * model coeff
    indicators = []
    if hasattr(model, 'coef_'):
        feature_names = vectorizer.get_feature_names_out()
        coef = model.coef_[0]
        
        # Get active features in the document
        indices = vec.indices
        
        # Calculate impact of each feature
        impacts = [(feature_names[i], coef[i] * vec[0, i]) for i in indices]
        
        if label == "positive":
            # Sort by highest positive impact
            impacts.sort(key=lambda x: x[1], reverse=True)
        else:
            # Sort by highest negative impact
            impacts.sort(key=lambda x: x[1])
            
        indicators = [item[0].replace('_NEG', ' (negated)') for item in impacts[:5] if abs(item[1]) > 0.1]
        
    return {
        "label": label,
        "confidence": round(confidence, 2),
        "indicators": indicators
    }
