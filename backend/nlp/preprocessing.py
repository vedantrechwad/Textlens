import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import string

# Ensure resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
# Remove negation words from stop words so we don't lose sentiment context
negation_words = {'not', 'no', 'never', 'nor', 'none', 'neither', 'cannot', "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "won't", "wouldn't", "don't", "doesn't", "didn't", "can't", "couldn't", "shouldn't", "mightn't", "mustn't"}
stop_words = stop_words - negation_words

lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """
    Cleans text by removing URLs, mentions, hashtags, and lowering case.
    """
    text = text.lower()
    text = re.sub(r'http\S+', '', text) # URLs
    text = re.sub(r'@\w+', '', text) # Mentions
    text = re.sub(r'#\w+', '', text) # Hashtags
    return text.strip()

def handle_negation(tokens):
    """
    Appends _NEG to tokens following a negation word until punctuation.
    """
    negation_flag = False
    result = []
    for token in tokens:
        if token in negation_words:
            negation_flag = True
            result.append(token)
            continue
        if token in string.punctuation:
            negation_flag = False
        
        if negation_flag and token not in string.punctuation:
            result.append(token + "_NEG")
        else:
            result.append(token)
    return result

def preprocess_for_sentiment(text: str) -> str:
    """
    Full preprocessing pipeline for sentiment analysis:
    clean -> tokenize -> negation handling -> remove punctuation & stopwords -> lemmatize
    """
    text = clean_text(text)
    tokens = word_tokenize(text)
    tokens = handle_negation(tokens)
    
    clean_tokens = []
    for t in tokens:
        # Check if t or its base (without _NEG) is punctuation/stopword
        base_t = t.replace("_NEG", "")
        if base_t not in string.punctuation and base_t not in stop_words:
            lemma = lemmatizer.lemmatize(base_t)
            if t.endswith("_NEG"):
                clean_tokens.append(lemma + "_NEG")
            else:
                clean_tokens.append(lemma)
                
    return " ".join(clean_tokens)

def get_sentences(text: str) -> list:
    """
    Segments text into sentences.
    """
    return sent_tokenize(text)
