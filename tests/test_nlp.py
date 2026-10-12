import pytest
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.nlp.preprocessing import clean_text, handle_negation
from backend.nlp.summarizer import summarize

def test_clean_text():
    raw = "Hello http://google.com @user #tag"
    assert clean_text(raw) == "hello"

def test_handle_negation():
    tokens = ["this", "is", "not", "good", "."]
    res = handle_negation(tokens)
    assert "good_NEG" in res
    assert "." in res

def test_summarization():
    text = "The quick brown fox jumps over the lazy dog. It was a very lazy dog indeed. This is a third sentence to ensure we have enough."
    summary = summarize(text, num_sentences=1)
    assert len(summary) > 0
    assert summary in text

def test_genz_decoding():
    from backend.nlp.genz_translator import decode_genz_text
    sample = "Bro that burger was bussin no cap fr fr!"
    result = decode_genz_text(sample)
    assert result["has_slang"] is True
    assert result["term_count"] >= 3
    assert "bussin" in [t["term"] for t in result["detected_terms"]]
    assert "no cap" in [t["term"] for t in result["detected_terms"]]
    assert "exceptionally delicious" in result["plain_english"]

def test_slang_aware_sentiment():
    from backend.nlp.sentiment import analyze_sentiment
    positive_slang = "The design is goated and bussin!"
    pos_res = analyze_sentiment(positive_slang)
    assert pos_res["label"] == "positive"
    assert any(term in pos_res["indicators"] for term in ["goated", "bussin"])

    negative_slang = "Bro got caught in 4k and is cooked."
    neg_res = analyze_sentiment(negative_slang)
    assert neg_res["label"] == "negative"
    assert any(term in neg_res["indicators"] for term in ["cooked", "caught in 4k"])

def test_language_detection():
    from backend.nlp.multilingual import detect_language
    french_text = "Bonjour, ceci est un test de langue française."
    lang_info = detect_language(french_text)
    assert lang_info["code"] == "fr"
    assert lang_info["is_english"] is False
    assert lang_info["name"] == "French"

