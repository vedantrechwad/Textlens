# NLP Algorithms and Methodology

This document explains the core classical NLP techniques used in the **NLP Lens** project.

## 1. Text Preprocessing
Before any machine learning models can process text, it must be cleaned and transformed.
- **Tokenization**: The process of splitting raw text into smaller units (tokens), such as sentences (`sent_tokenize`) or words (`word_tokenize`).
- **Stopword Removal**: Words that carry little semantic meaning (like "the", "is", "at") are removed using NLTK's predefined stopword lists to reduce noise.
- **Lemmatization**: Reducing words to their base or dictionary form (e.g., "running" becomes "run", "better" becomes "good"). This normalizes the text and reduces the vocabulary size.
- **Negation Handling**: In sentiment analysis, words following a negation ("not", "no") often have their meaning flipped. We handle this by appending a `_NEG` suffix to tokens following a negation word until the next punctuation mark (e.g., "not good" -> "good_NEG").

## 2. Feature Extraction (TF-IDF)
**Term Frequency-Inverse Document Frequency (TF-IDF)** is used to convert text into numerical vectors. 
- **TF (Term Frequency)**: Measures how frequently a term occurs in a document.
- **IDF (Inverse Document Frequency)**: Measures how important a term is across the entire corpus. Words that appear in many documents (e.g., "the") receive a lower weight, while rare, highly descriptive words receive a higher weight.

## 3. Sentiment Classification (Support Vector Machines)
We use a **Linear Support Vector Machine (Linear SVM)** for binary sentiment classification.
- An SVM finds the optimal hyperplane that separates positive and negative examples in high-dimensional space.
- It maximizes the margin between the two classes.
- Linear SVM is computationally efficient and highly effective for sparse, high-dimensional text data (like TF-IDF vectors).

## 4. TextRank Summarization
**TextRank** is a graph-based ranking algorithm inspired by Google's PageRank, used here for extractive summarization.
1. **Segmentation**: The text is split into sentences.
2. **Vectorization**: Each sentence is converted to a TF-IDF vector.
3. **Similarity Graph**: We calculate the **Cosine Similarity** between every pair of sentence vectors to build a similarity matrix.
4. **Graph Representation**: Sentences are nodes, and similarity scores are edges.
5. **PageRank**: The PageRank algorithm is run on this graph to find the most "central" or "important" sentences.
6. **Extraction**: The top-ranked sentences are selected and reordered chronologically to form the summary.

## 5. Named Entity Recognition (NER)
NER is the task of identifying and classifying key entities in text into predefined categories (e.g., PERSON, ORGANIZATION, LOCATION).
We use **spaCy's** pre-trained `en_core_web_sm` model, which uses a Convolutional Neural Network (CNN) architecture with word embeddings to predict entity boundaries and labels.
