import pandas as pd
import re
import nltk
import grpc
import morphology_pb2
import morphology_pb2_grpc
from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = set(stopwords.words('turkish'))

channel = grpc.insecure_channel('localhost:6789')
stub = morphology_pb2_grpc.MorphologyServiceStub(channel)

def normalize_text(text):
    text = text.replace("ı", "i").replace("ğ", "g").replace("ü", "u")
    text = text.replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return text

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = normalize_text(text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

def lemmatize_text(text):
    if not isinstance(text, str) or text.strip() == "":
        return ""

    words = text.split()
    lemmatized_words = []

    for word in words:
        try:
            request = morphology_pb2.WordAnalysisRequest(input=word)
            response = stub.AnalyzeWord(request)

            if response and response.analyses:
                best_lemma = response.analyses[0].dictionaryItem.lemma if response.analyses[0].dictionaryItem.lemma else word
                lemmatized_words.append(best_lemma)
            else:
                lemmatized_words.append(word)

        except Exception as e:
            lemmatized_words.append(word)

    return ' '.join(lemmatized_words)


def process_csv(file_name, output_file_name):
    try:
        df = pd.read_csv(file_name)

        comment_column = "content" if "content" in df.columns else "review"

        df = df.dropna(subset=[comment_column])

        df["cleaned_content"] = df[comment_column].apply(clean_text)

        df["lemmatized_content"] = df["cleaned_content"].apply(lemmatize_text)

        df.to_csv(output_file_name, index=False)
    except Exception as e:
        print(f"❌ Hata: {e}")

process_csv("google_play.csv", "cleaned_google_play.csv")
process_csv("app_store.csv", "cleaned_app_store.csv")
