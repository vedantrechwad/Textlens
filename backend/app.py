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
from backend.nlp.genz_translator import decode_genz_text
from backend.nlp.multilingual import detect_language, translate_text, translate_to_target
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
        "statistics": True,
        "genz": True,
        "multilingual": True
    })
    
    target_language = options.get("target_language", "en")
    logger.info(f"Processing text of length {len(text)}")

    # 1. Multilingual Language Detection
    lang_info = detect_language(text)
    was_translated = False
    english_text = text
    
    if not lang_info["is_english"] and options.get("multilingual", True):
        logger.info(f"Foreign language detected: {lang_info['name']} ({lang_info['code']}). Translating to English for NLP pipeline.")
        trans_res = translate_text(text, source_code=lang_info["code"], target_code="en")
        if trans_res.get("was_translated") and trans_res.get("translated_text"):
            english_text = trans_res["translated_text"]
            was_translated = True

    # 2. Gen-Z Slang Decoding (runs on English text)
    genz_info = None
    if options.get("genz", True):
        genz_info = decode_genz_text(english_text)

    # 3. NLP Pipeline
    analysis_text = english_text
    
    summary_result = summarize(analysis_text) if options.get("summary", True) else None
    
    # If user requested summary in a target foreign language
    translated_summary = None
    if summary_result and target_language and target_language != "en":
        try:
            translated_summary = translate_to_target(summary_result, target_language)
        except Exception as e:
            logger.warning(f"Target language summary translation failed: {e}")

    result = {
        "success": True,
        "language": {
            "detected_code": lang_info["code"],
            "detected_name": lang_info["name"],
            "confidence": lang_info["confidence"],
            "is_english": lang_info["is_english"],
            "was_translated": was_translated,
            "translated_to_english": english_text if was_translated else None
        },
        "genz": genz_info,
        "sentiment": analyze_sentiment(analysis_text, options.get("sentiment_model", "vader")) if options.get("sentiment", True) else None,
        "summary": summary_result,
        "translated_summary": translated_summary,
        "keywords": extract_keywords(analysis_text) if options.get("keywords", True) else None,
        "entities": extract_entities(analysis_text) if options.get("entities", True) else None,
        "pos": get_pos_tags(analysis_text) if options.get("pos", True) else None,
        "statistics": calculate_statistics(text) if options.get("statistics", True) else None
    }
    
    return jsonify(result), 200


@app.route('/api/genz-decode', methods=['POST'])
def genz_decode():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Missing 'text' in request body"}), 400
    text = data['text']
    result = decode_genz_text(text)
    return jsonify({"success": True, "genz": result}), 200


@app.route('/api/genz-glossary', methods=['GET'])
def genz_glossary():
    from backend.nlp.genz_translator import GENZ_DICTIONARY
    terms = []
    for term, meta in sorted(GENZ_DICTIONARY.items()):
        terms.append({
            "term": term,
            "translation": meta["translation"],
            "definition": meta["definition"],
            "category": meta["category"],
            "sentiment_score": meta["sentiment_score"]
        })
    return jsonify({"success": True, "count": len(terms), "glossary": terms}), 200


@app.route('/api/translate', methods=['POST'])
def translate_api():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "Missing 'text' in request body"}), 400
    text = data['text']
    source = data.get('source_code', 'auto')
    target = data.get('target_code', 'en')
    result = translate_text(text, source_code=source, target_code=target)
    return jsonify({"success": True, "translation": result}), 200


if __name__ == '__main__':
    app.run(debug=Config.DEBUG_MODE, port=5000)
