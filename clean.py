import pandas as pd
import re
import nltk
import grpc
import morphology_pb2
import morphology_pb2_grpc
from nltk.corpus import stopwords

# Download Turkish stopwords
nltk.download('stopwords')
language = None

# gRPC channel and stub for morphology service
channel = grpc.insecure_channel('localhost:6789')
stub = morphology_pb2_grpc.MorphologyServiceStub(channel)

# Clean text by converting to lowercase, normalizing, removing punctuation, digits, and stopwords.
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)      # Remove digits
    text = ' '.join(word for word in text.split() if word not in (set(stopwords.words('turkish')) if language == "tr" else set(stopwords.words('english'))))  # Remove stopwords
    return text

# Lemmatize text using the gRPC morphology service.
def lemmatize_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""

    lemmatized_words = []
    for word in text.split():
        try:
            # Send word to morphology service
            request = morphology_pb2.WordAnalysisRequest(input=word)
            response = stub.AnalyzeWord(request)

            # Use the lemma if available, otherwise keep the original word
            if response and response.analyses:
                lemma = response.analyses[0].dictionaryItem.lemma or word
                lemmatized_words.append(lemma)
            else:
                lemmatized_words.append(word)
        except Exception:
            lemmatized_words.append(word)  # Fallback to original word on error

    return ' '.join(lemmatized_words)

# Process a DataFrame by cleaning and lemmatizing the 'text' column.
def process_dataframe(df, lang):
    global language
    try:
        language = lang
        # Drop rows with missing 'text' values
        df = df.dropna(subset=["text"])

        # Apply cleaning and lemmatization
        df["text"] = df["text"].apply(clean_text)
        df["text"] = df["text"].apply(lemmatize_text)

        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return df