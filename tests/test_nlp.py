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
