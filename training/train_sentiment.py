import os
import sys
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import movie_reviews

# Ensure NLTK datasets are present
try:
    nltk.data.find('corpora/movie_reviews')
except LookupError:
    nltk.download('movie_reviews')

# Add backend to path to import config and preprocessing
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.config import Config
from backend.nlp.preprocessing import preprocess_for_sentiment

def load_data():
    print("Loading NLTK Movie Reviews dataset...")
    documents = []
    labels = []
    
    for category in movie_reviews.categories():
        for fileid in movie_reviews.fileids(category):
            # Read the raw text of the review
            text = movie_reviews.raw(fileid)
            documents.append(text)
            labels.append(category) # 'pos' or 'neg'
            
    return documents, labels

def main():
    docs, labels = load_data()
    print(f"Loaded {len(docs)} reviews.")
    
    # Map labels to binary
    label_map = {'pos': 1, 'neg': 0}
    y = [label_map[label] for label in labels]
    
    print("Preprocessing text... (this might take a few moments)")
    # We will use the custom preprocessing pipeline
    X_processed = [preprocess_for_sentiment(doc) for doc in docs]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42)
    
    # Feature extraction: TF-IDF
    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    models = {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Linear SVM": LinearSVC(random_state=42)
    }
    
    best_model = None
    best_acc = 0
    best_name = ""
    
    print("\n--- Model Evaluation ---")
    for name, model in models.items():
        model.fit(X_train_vec, y_train)
        preds = model.predict(X_test_vec)
        acc = accuracy_score(y_test, preds)
        print(f"{name} Accuracy: {acc:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_name = name
            
    print(f"\nBest Model: {best_name} with Accuracy {best_acc:.4f}")
    
    # Save the best model and vectorizer
    os.makedirs(Config.MODELS_DIR, exist_ok=True)
    
    with open(Config.SENTIMENT_MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)
        
    with open(Config.TFIDF_VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print(f"Saved best model to {Config.SENTIMENT_MODEL_PATH}")
    print(f"Saved TF-IDF vectorizer to {Config.TFIDF_VECTORIZER_PATH}")
    print("Done!")

if __name__ == "__main__":
    main()
