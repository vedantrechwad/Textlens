from backend.nlp.preprocessing import get_sentences
from nltk.tokenize import word_tokenize

def calculate_statistics(text: str) -> dict:
    if not text.strip():
        return {
            "characters": 0,
            "words": 0,
            "sentences": 0,
            "avgSentenceLength": 0,
            "readingComplexity": "Simple"
        }
        
    chars = len(text)
    words = word_tokenize(text)
    num_words = len([w for w in words if w.isalnum()])
    sentences = get_sentences(text)
    num_sentences = len(sentences)
    
    avg_sentence_len = num_words / num_sentences if num_sentences > 0 else 0
    
    # Very basic reading complexity estimate based on avg sentence length
    complexity = "Simple"
    if avg_sentence_len > 15:
        complexity = "Moderate"
    if avg_sentence_len > 25:
        complexity = "Complex"
        
    return {
        "characters": chars,
        "words": num_words,
        "sentences": num_sentences,
        "avgSentenceLength": round(avg_sentence_len, 1),
        "readingComplexity": complexity
    }
