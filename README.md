# Textlens

> **Understand the meaning behind what you're reading.**

Textlens is a Chrome Extension and Python Flask backend that allows you to select text on any webpage (or analyze the entire page) to extract meaningful insights using classical Natural Language Processing techniques. 

This project was built for an academic NLP course to demonstrate traditional NLP pipelines without relying on LLMs.

## Features

- **Analyze Selected Text**: Highlight text, right-click, and analyze.
- **Analyze Page/Thread**: Extract visible text from articles or discussion threads.
- **Sentiment Analysis**: Classification (Positive/Negative) with confidence scores and key indicators (using Linear SVM + TF-IDF).
- **Extractive Summarization**: TextRank algorithm built from scratch using cosine similarity and PageRank.
- **Keyword Extraction**: Unigram and bigram extraction using TF-IDF.
- **Named Entity Recognition**: Identifies organizations, people, and locations using spaCy.
- **Text Statistics**: Basic character/word counts and POS (Part of Speech) tagging distributions.
- **Show NLP Pipeline Mode**: A special UI toggle that explains the step-by-step NLP transformations for academic demonstrations and vivas.

## Architecture

```text
Chrome Extension (Manifest V3)
       │
       │ HTTP REST API (JSON)
       ▼
Flask Backend (Python)
       │
       ├─► Preprocessing (Tokenization, Lemmatization, Stopwords)
       ├─► Sentiment Classification (Linear SVM)
       ├─► Summarization (TextRank Graph Algorithm)
       ├─► NER & POS (spaCy, NLTK)
       │
       ▼
JSON Response
```

## Technology Stack

- **Frontend**: HTML, CSS, Vanilla JavaScript, Chrome Extension Manifest V3.
- **Backend**: Python, Flask, Flask-CORS.
- **NLP Libraries**: `nltk`, `spacy`, `scikit-learn`, `networkx`.
- **Machine Learning**: TF-IDF Vectorization, Linear SVM.

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
5. View the results. Toggle **Show NLP Pipeline Mode** to see the exact steps the text went through in the backend.

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
