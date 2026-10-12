# Textlens

> **Understand the meaning behind what you're reading.**

Textlens is a Chrome Extension and Python Flask backend that allows you to select text on any webpage (or analyze the entire page) to extract meaningful insights using classical Natural Language Processing techniques. 

This project was built for an academic NLP course to demonstrate traditional NLP pipelines without relying on LLMs.

## Features

- **Gen-Z Lingo to Normal English Decoder**: Detects 100+ Gen-Z slang terms, brainrot phrases, and social media acronyms (`bussin`, `no cap`, `rizz`, `cooked`, `slay`, `crash out`, `delulu`, etc.), displays plain English definitions, and translates sentences into Standard English.
- **Slang-Aware Sentiment Analysis**: VADER lexicon calibrated with Gen-Z slang sentiment weights (scoring `bussin` and `goated` as positive, and `cap` and `cooked` as negative) with highlighted key indicators.
- **Multilingual Support**:
  - **Auto Language Detection**: Identifies 50+ languages (French, Spanish, Hindi, German, Japanese, Chinese, etc.) with confidence scores.
  - **Foreign Text to English Translation**: Seamlessly translates foreign text into English so classical NLP pipelines (sentiment, summarization, keywords, NER) function on any language.
  - **Target Language Summary Translation**: Translate the generated TL;DR summary into user-selected target languages (Spanish, French, Hindi, German, Japanese, etc.).
- **Analyze Selected Text / Quick Input**: Highlight text, right-click, or type/paste text directly in the extension popup.
- **Analyze Page/Thread**: Extract visible text from articles or discussion threads (Reddit, X/Twitter, Quora).
- **Extractive Summarization**: TextRank algorithm built using cosine similarity and PageRank.
- **Keyword Extraction**: Unigram and bigram extraction using TF-IDF.
- **Named Entity Recognition**: Identifies organizations, people, and locations using spaCy.
- **Text Statistics**: Basic character/word counts, readability complexity, and POS (Part of Speech) tagging distributions.

## Architecture

```text
Chrome Extension (Manifest V3)
       │
       │ HTTP REST API (JSON)
       ▼
Flask Backend (Python)
       │
       ├─► Language Detection & Auto-Translation (langdetect, deep-translator)
       ├─► Gen-Z Slang Decoding & Standard English Translation
       ├─► Preprocessing (Tokenization, Lemmatization, Stopwords)
       ├─► Slang-Aware Sentiment Analysis (VADER / DistilBERT)
       ├─► Summarization (TextRank Graph Algorithm)
       ├─► NER & POS (spaCy, NLTK)
       │
       ▼
JSON Response (Language, Slang Decoder, Sentiment, TL;DR, Keywords, Entities)
```

## Technology Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript, Chrome Extension Manifest V3.
- **Backend**: Python, Flask, Flask-CORS.
- **NLP & Multilingual**: `nltk`, `spacy`, `scikit-learn`, `networkx`, `deep-translator`, `langdetect`.
- **Machine Learning & Lexicons**: TF-IDF Vectorization, Linear SVM, VADER + Gen-Z Sentiment Lexicon.

## Dataset & Model Training

The sentiment model is trained on the **NLTK Movie Reviews** dataset (2000 documents). 

- **Preprocessing**: Lowercasing, URL/mention removal, punctuation handling, negation handling (appending `_NEG` to negated words), stopword removal, and WordNet lemmatization.
- **Features**: TF-IDF (1-2 n-grams, max 10000 features).
- **Evaluation**: The script compares Naive Bayes, Logistic Regression, and Linear SVM, saving the best model to the backend. In local tests, Linear SVM achieved ~84.5% accuracy.

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repository>
cd textlens
```

### 2. Setup Python Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Train the Model
This will download the dataset, preprocess it, evaluate models, and save the best one.
```bash
python training/train_sentiment.py
```

### 5. Start the Flask Backend
```bash
python backend/app.py
```
The server will start on `http://127.0.0.1:5000`.

### 6. Install Chrome Extension
1. Open Google Chrome and go to `chrome://extensions`.
2. Enable **Developer mode** in the top right.
3. Click **Load unpacked**.
4. Select the `extension/` folder from this repository.

## Usage / Demonstration
1. Ensure the Flask server is running.
2. Go to any text-heavy webpage (e.g., Wikipedia, Reddit).
3. Select a paragraph of text, right-click, and choose **Analyze with Textlens**.
4. Alternatively, click the Textlens icon in the Chrome toolbar and click **Analyze Page**.
5. View the results.

## Academic Concepts Demonstrated

- **Tokenization**: Breaking text into sentences and words (`nltk.word_tokenize`).
- **Stopwords & Lemmatization**: Removing common meaningless words and reducing words to their dictionary roots (`WordNetLemmatizer`).
- **Negation Handling**: Properly treating words following "not" as negated (e.g., `good_NEG`).
- **TF-IDF**: Term Frequency-Inverse Document Frequency for feature weighting.
- **Linear SVM**: A robust maximum-margin classifier for high-dimensional text data.
- **TextRank**: Graph-based ranking model for text processing (similar to Google's PageRank) used here for extractive summarization.
- **NER & POS Tagging**: Extracting structural and semantic meaning from unstructured text.

## Privacy
Textlens processes text entirely through your local Flask backend. No text is sent to third-party AI APIs (no LLMs are used).

## Future Improvements
- Train on larger datasets (e.g., Sentiment140) for generalized social media analysis.
- Add Emotion classification (Joy, Anger, Sadness).
- Implement Aspect-based Sentiment Analysis.
