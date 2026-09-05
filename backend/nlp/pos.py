import nltk
from nltk.tokenize import word_tokenize

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

def get_pos_tags(text: str) -> dict:
    """
    Returns POS distribution using NLTK.
    """
    if not text.strip():
        return {}
        
    tokens = word_tokenize(text)
    tags = nltk.pos_tag(tokens)
    
    pos_counts = {
        "Nouns": 0,
        "Verbs": 0,
        "Adjectives": 0,
        "Adverbs": 0
    }
    
    for _, tag in tags:
        if tag.startswith('NN'):
            pos_counts["Nouns"] += 1
        elif tag.startswith('VB'):
            pos_counts["Verbs"] += 1
        elif tag.startswith('JJ'):
            pos_counts["Adjectives"] += 1
        elif tag.startswith('RB'):
            pos_counts["Adverbs"] += 1
            
    return pos_counts
