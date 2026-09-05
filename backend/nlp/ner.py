import spacy

# Load spaCy model lazily to save memory if NER isn't called,
# but since we want fast API responses, it's better to load once.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: en_core_web_sm not found. Run 'python -m spacy download en_core_web_sm'")
    nlp = None

def extract_entities(text: str) -> list:
    """
    Extracts named entities using spaCy.
    """
    if not nlp or not text.strip():
        return []
        
    doc = nlp(text)
    entities_list = []
    seen = set()
    
    for ent in doc.ents:
        # Avoid duplicates for the simple UI
        if ent.text.lower() not in seen:
            seen.add(ent.text.lower())
            entities_list.append({
                "text": ent.text,
                "label": ent.label_
            })
            
    return entities_list
