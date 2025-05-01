import pandas as pd
import re
import nltk
import grpc
import morphology_pb2
import morphology_pb2_grpc
from nltk.corpus import stopwords

# Download Turkish stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('turkish'))

# gRPC channel and stub for morphology service
channel = grpc.insecure_channel('localhost:6789')
stub = morphology_pb2_grpc.MorphologyServiceStub(channel)

# Normalize Turkish characters to their Latin equivalents.
def normalize_text(text):
    replacements = {
        "ı": "i", "ğ": "g", "ü": "u",
        "ş": "s", "ö": "o", "ç": "c"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# Clean text by converting to lowercase, normalizing, removing punctuation, digits, and stopwords.
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # text = normalize_text(text)
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)      # Remove digits
    text = ' '.join(word for word in text.split() if word not in stop_words)  # Remove stopwords
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
def process_dataframe(df):
    try:
        # Drop rows with missing 'text' values
        df = df.dropna(subset=["text"])

        # Apply cleaning and lemmatization
        df["text"] = df["text"].apply(clean_text)
        df["text"] = df["text"].apply(lemmatize_text)

        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return df