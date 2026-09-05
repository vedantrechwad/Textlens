from sklearn.feature_extraction.text import TfidfVectorizer
from backend.nlp.preprocessing import clean_text

def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    Extracts top keywords/phrases using TF-IDF.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=100)
        tfidf_matrix = vectorizer.fit_transform([cleaned])
        
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Pair up feature names with their scores
        keywords_scores = list(zip(feature_names, tfidf_scores))
        
        # Sort by score in descending order
        keywords_scores.sort(key=lambda x: x[1], reverse=True)
        
        result = []
        for term, score in keywords_scores[:top_n]:
            if score > 0.0:
                result.append({
                    "term": term,
                    "score": round(float(score), 2)
                })
        return result
    except Exception as e:
        print(f"Keyword extraction error: {e}")
        return []
