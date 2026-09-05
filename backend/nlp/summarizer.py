import math
import networkx as nx
from backend.nlp.preprocessing import get_sentences, clean_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.config import Config

def summarize(text: str, num_sentences: int = None) -> str:
    """
    Extractive summarization using TextRank algorithm.
    """
    sentences = get_sentences(text)
    if not sentences:
        return ""
        
    # If the text is very short, just return it
    if len(sentences) <= 2:
        return text
        
    if num_sentences is None:
        num_sentences = Config.DEFAULT_SUMMARY_SENTENCES
        # Adaptive length
        if len(sentences) <= 5:
            num_sentences = 1
        elif len(sentences) <= 15:
            num_sentences = 2
        elif len(sentences) <= 30:
            num_sentences = 3
        else:
            num_sentences = max(3, int(len(sentences) * 0.1))
            
    num_sentences = min(num_sentences, len(sentences) - 1)
    
    # Preprocess sentences for similarity matching
    clean_sentences = [clean_text(s) for s in sentences]
    
    # Check if empty after cleaning
    clean_sentences = [s if s else "empty_sentence" for s in clean_sentences]

    try:
        # 1. TF-IDF Vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(clean_sentences)
        
        # 2. Cosine Similarity Matrix
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # 3. Create Graph and run PageRank (TextRank)
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        
        # 4. Rank sentences
        ranked_sentences = sorted(((scores[i], i, s) for i, s in enumerate(sentences)), reverse=True)
        
        # 5. Select top N sentences
        top_n = ranked_sentences[:num_sentences]
        
        # 6. Restore original order
        top_n.sort(key=lambda x: x[1])
        
        summary = " ".join([item[2] for item in top_n])
        return summary
    except Exception as e:
        print(f"Summarization error: {e}")
        # Fallback to first few sentences
        return " ".join(sentences[:num_sentences])
