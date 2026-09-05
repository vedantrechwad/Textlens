import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')
    SENTIMENT_MODEL_PATH = os.path.join(MODELS_DIR, 'sentiment_model.pkl')
    TFIDF_VECTORIZER_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    
    MAX_TEXT_LENGTH = 50000
    DEBUG_MODE = True
    
    # Defaults for NLP
    DEFAULT_SUMMARY_SENTENCES = 3
