import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.nlp.sentiment import analyze_sentiment
from backend.nlp.summarizer import summarize
from backend.nlp.keywords import extract_keywords
from backend.nlp.ner import extract_entities
from backend.nlp.pos import get_pos_tags
from backend.nlp.statistics import calculate_statistics
import logging

app = Flask(__name__)
CORS(app)

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("textlens")


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Missing 'text' in request body"}), 400
        
    text = data['text']
    
    if not text.strip():
        return jsonify({"success": False, "error": "Text cannot be empty."}), 400
        
    if len(text) > Config.MAX_TEXT_LENGTH:
        return jsonify({"success": False, "error": f"Text too long. Max length is {Config.MAX_TEXT_LENGTH} characters."}), 413

    options = data.get('options', {
        "sentiment": True,
        "summary": True,
        "keywords": True,
        "entities": True,
        "pos": True,
        "statistics": True
    })
    
    logger.info(f"Processing text of length {len(text)}")
    
    result = {
        "success": True,
        "sentiment": analyze_sentiment(text) if options.get("sentiment") else None,
        "summary": summarize(text) if options.get("summary") else None,
        "keywords": extract_keywords(text) if options.get("keywords") else None,
        "entities": extract_entities(text) if options.get("entities") else None,
        "pos": get_pos_tags(text) if options.get("pos") else None,
        "statistics": calculate_statistics(text) if options.get("statistics") else None
    }
    
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=Config.DEBUG_MODE, port=5000)
