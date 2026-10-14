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


def test_contextual_slang_distinction():
    from backend.nlp.genz_translator import decode_genz_text
    sentence = "I was literally sipping my iced matcha tea while Sarah spilled the absolute tea about why her situationship ended."
    result = decode_genz_text(sentence)
    assert result["has_slang"] is True
    terms = {t["term"]: t for t in result["detected_terms"]}
    assert "tea" in terms
    assert len(terms["tea"]["spans"]) == 1
    start, end = terms["tea"]["spans"][0]
    assert sentence[start:end].lower() == "tea"
    assert start > 50, "Only gossip tea should be matched, not beverage tea at the start"
    assert "iced matcha tea" in result["plain_english"]
    assert "gossip and juicy scoop" in result["plain_english"]


def test_all_polysemous_slang_disambiguation():
    from backend.nlp.genz_translator import decode_genz_text
    test_cases = [
        ("I cooked dinner for my friends, but bro I am cooked for the finals tomorrow.", "cooked", "I cooked dinner"),
        ("He was wearing a baseball cap while telling a story that was pure cap.", "cap", "baseball cap"),
        ("I go to the gym to stay fit, but that fit today is fire.", "fit", "stay fit"),
        ("The salty soup made me thirsty, but he was salty about losing the match.", "salty", "salty soup"),
        ("I ate a healthy snack, but she looked like a snack in that outfit.", "snack", "healthy snack"),
        ("I lost a 50 dollar bet at the casino, but if you want to hang out, bet.", "bet", "50 dollar bet"),
        ("They shook hands after the game, but I was shook by that ending.", "shook", "shook hands")
    ]
    for sentence, target_term, literal_substr in test_cases:
        res = decode_genz_text(sentence)
        terms = {t["term"]: t for t in res["detected_terms"]}
        assert target_term in terms, f"Slang '{target_term}' should be detected in: {sentence}"
        assert len(terms[target_term]["spans"]) == 1, f"Only 1 slang occurrence should be matched for '{target_term}' in: {sentence}"
        assert literal_substr in res["plain_english"], f"Literal phrase '{literal_substr}' should be preserved intact in: {res['plain_english']}"



