"""
Multilingual Support Module for Textlens.
Provides automatic language detection, translation to English for unified NLP analysis,
and translation of analysis results/summaries into user-selected target languages.
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("textlens.multilingual")

# Graceful import for langdetect
try:
    import langdetect
    from langdetect import DetectorFactory
    DetectorFactory.seed = 0
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False
    logger.warning("langdetect not installed. Falling back to heuristic language detection.")

# Graceful import for deep_translator
try:
    from deep_translator import MyMemoryTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False
    logger.warning("deep-translator not installed. Multilingual translation disabled.")

# Mapping of ISO 639-1 language codes to descriptive names and MyMemory source identifiers
LANG_CODE_TO_NAME: Dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "ja": "Japanese",
    "zh-cn": "Chinese",
    "zh": "Chinese",
    "ru": "Russian",
    "ar": "Arabic",
    "ko": "Korean",
    "nl": "Dutch",
    "tr": "Turkish",
    "pl": "Polish",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "el": "Greek",
    "sv": "Swedish",
    "cs": "Czech",
    "da": "Danish",
    "fi": "Finnish",
    "he": "Hebrew",
    "no": "Norwegian",
    "ro": "Romanian",
    "th": "Thai",
    "uk": "Ukrainian",
    "ur": "Urdu"
}

# Mapping to MyMemory language names
CODE_TO_MYMEMORY: Dict[str, str] = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "pt": "portuguese",
    "hi": "hindi",
    "mr": "marathi",
    "bn": "bengali",
    "ta": "tamil india",
    "te": "telugu",
    "ja": "japanese",
    "zh-cn": "chinese simplified",
    "zh": "chinese simplified",
    "ru": "russian",
    "ar": "arabic",
    "ko": "korean",
    "nl": "dutch",
    "tr": "turkish",
    "pl": "polish",
    "vi": "vietnamese",
    "id": "indonesian",
    "el": "greek",
    "sv": "swedish",
    "cs": "czech",
    "da": "danish",
    "fi": "finnish",
    "he": "hebrew",
    "no": "norwegian bokmål",
    "ro": "romanian",
    "th": "thai",
    "uk": "ukrainian",
    "ur": "urdu"
}


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detects the language of the given text using langdetect with script heuristics as fallback.
    Returns:
      {
        "code": "es",
        "name": "Spanish",
        "confidence": 0.99,
        "is_english": False
      }
    """
    if not text or not text.strip():
        return {
            "code": "en",
            "name": "English",
            "confidence": 1.0,
            "is_english": True
        }

    clean_sample = re.sub(r'http\S+|[0-9#@!$%^&*()_+=\-\[\]{}|\\:;"\'<>,.?/~`]', '', text).strip()
    
    # If the text is very short or primarily symbols/numbers, check script heuristics
    if len(clean_sample) < 3:
        # Script heuristics
        if re.search(r'[\u0900-\u097F]', text):
            return {"code": "hi", "name": "Hindi", "confidence": 0.95, "is_english": False}
        if re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text):
            return {"code": "ja", "name": "Japanese / CJK", "confidence": 0.90, "is_english": False}
        if re.search(r'[\u0400-\u04FF]', text):
            return {"code": "ru", "name": "Russian", "confidence": 0.90, "is_english": False}
        if re.search(r'[\u0600-\u06FF]', text):
            return {"code": "ar", "name": "Arabic", "confidence": 0.90, "is_english": False}
        return {"code": "en", "name": "English", "confidence": 1.0, "is_english": True}

    if HAS_LANGDETECT:
        try:
            predictions = langdetect.detect_langs(clean_sample)
            if predictions:
                best = predictions[0]
                code = best.lang.lower()
                conf = round(best.prob, 2)
                name = LANG_CODE_TO_NAME.get(code, code.capitalize())
                return {
                    "code": code,
                    "name": name,
                    "confidence": conf,
                    "is_english": (code == "en")
                }
        except Exception as e:
            logger.warning(f"Language detection fallback triggered: {e}")

    # Heuristic fallback if langdetect raised error
    if re.search(r'[\u0900-\u097F]', text):
        return {"code": "hi", "name": "Hindi", "confidence": 0.95, "is_english": False}
    if re.search(r'[\u3040-\u30ff]', text):
        return {"code": "ja", "name": "Japanese", "confidence": 0.95, "is_english": False}
    if re.search(r'[\u4e00-\u9fff]', text):
        return {"code": "zh", "name": "Chinese", "confidence": 0.95, "is_english": False}
    if re.search(r'[\u0400-\u04FF]', text):
        return {"code": "ru", "name": "Russian", "confidence": 0.95, "is_english": False}
    if re.search(r'[\u0600-\u06FF]', text):
        return {"code": "ar", "name": "Arabic", "confidence": 0.95, "is_english": False}

    return {
        "code": "en",
        "name": "English",
        "confidence": 1.0,
        "is_english": True
    }


def _split_into_chunks(text: str, max_chars: int = 400) -> List[str]:
    """
    Splits text into chunks of at most max_chars, preferably at sentence or word boundaries.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    # Split by newlines or sentence terminators
    sentences = re.split(r'([.?!।\n]+)', text)
    current_chunk = ""

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        sep = sentences[i + 1] if i + 1 < len(sentences) else ""
        piece = sentence + sep
        if not piece.strip():
            continue

        if len(current_chunk) + len(piece) <= max_chars:
            current_chunk += piece
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If a single sentence exceeds max_chars, split by words
            if len(piece) > max_chars:
                words = piece.split()
                sub_chunk = ""
                for w in words:
                    if len(sub_chunk) + len(w) + 1 <= max_chars:
                        sub_chunk += (" " if sub_chunk else "") + w
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = w
                current_chunk = sub_chunk
            else:
                current_chunk = piece

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def translate_text(text: str, source_code: str = "auto", target_code: str = "en") -> Dict[str, Any]:
    """
    Translates text from source language to target language (defaults to English).
    Uses chunking to respect API length constraints.
    """
    if not text or not text.strip():
        return {
            "original_text": text,
            "translated_text": text,
            "was_translated": False,
            "source_code": source_code,
            "target_code": target_code
        }

    # If source is already target, return immediately
    if source_code == target_code or (source_code == "en" and target_code == "en"):
        return {
            "original_text": text,
            "translated_text": text,
            "was_translated": False,
            "source_code": source_code,
            "target_code": target_code
        }

    if not HAS_TRANSLATOR:
        return {
            "original_text": text,
            "translated_text": text,
            "was_translated": False,
            "error": "deep-translator library not installed",
            "source_code": source_code,
            "target_code": target_code
        }

    source_lang_name = CODE_TO_MYMEMORY.get(source_code, "autodetect")
    target_lang_name = CODE_TO_MYMEMORY.get(target_code, "english")

    chunks = _split_into_chunks(text, max_chars=400)
    translated_chunks = []

    try:
        translator = MyMemoryTranslator(source=source_lang_name, target=target_lang_name)
        for chunk in chunks:
            if not chunk.strip():
                continue
            translated = translator.translate(chunk)
            translated_chunks.append(translated if translated else chunk)

        joined_translation = " ".join(translated_chunks)
        return {
            "original_text": text,
            "translated_text": joined_translation,
            "was_translated": True,
            "source_code": source_code,
            "target_code": target_code
        }
    except Exception as e:
        logger.error(f"Translation failed ({source_code} -> {target_code}): {e}")
        return {
            "original_text": text,
            "translated_text": text,
            "was_translated": False,
            "error": str(e),
            "source_code": source_code,
            "target_code": target_code
        }


def translate_to_target(text: str, target_code: str) -> str:
    """
    Utility function to translate text (e.g. summary or output) to a user's chosen target language.
    """
    if not text or not text.strip() or target_code == "en":
        return text
    res = translate_text(text, source_code="en", target_code=target_code)
    return res.get("translated_text", text)
