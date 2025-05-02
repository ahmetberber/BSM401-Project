import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora, models
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

# NLTK setup
nltk.download("punkt")

# Read comments
df = pd.read_csv("comments.csv")
df = df.dropna(subset=["text"])
df["tokenized"] = df["text"].apply(lambda x: word_tokenize(str(x).lower()))
text_data = df["tokenized"].tolist()
raw_texts = df["text"].tolist()

# TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(tokenizer=word_tokenize, max_features=1000)
tfidf_matrix = tfidf_vectorizer.fit_transform(raw_texts)


# ----------------- LDA ----------------- #
def run_lda():
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]
    lda_model = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10)

    def get_lda_topic(text):
        bow = dictionary.doc2bow(word_tokenize(text.lower()))
        dist = lda_model[bow]
        return sorted(dist, key=lambda x: x[1], reverse=True)[0][0] if dist else None

    df["topic_lda"] = df["text"].apply(get_lda_topic)

    print("\n🔹 LDA Topics:")
    for idx, topic in lda_model.print_topics():
        print(f"Topic {idx + 1}: {topic}")

    return lda_model


# ----------------- LSA ----------------- #
def run_lsa():
    lsa_model = TruncatedSVD(n_components=5, random_state=42)
    lsa_topic_matrix = lsa_model.fit_transform(tfidf_matrix)
    df["topic_lsa"] = lsa_topic_matrix.argmax(axis=1)

    print("\n🔹 LSA Topic Terms:")
    terms = tfidf_vectorizer.get_feature_names_out()
    for i, comp in enumerate(lsa_model.components_):
        top_words = [terms[idx] for idx in comp.argsort()[-10:]]
        print(f"Topic {i + 1}: {' '.join(top_words)}")

    return lsa_model


# ----------------- BERT + KMeans ----------------- #
def run_bert():
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    embeddings = model.encode(raw_texts, show_progress_bar=True)

    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    df["topic_bert"] = clusters

    print("\n🔹 Number of BERT clusters:", len(set(clusters)))
    return clusters


# ----------------- Visualization ----------------- #
def plot_wordclouds(lda_model, lsa_model):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # LDA
    topic_words = dict(lda_model.show_topic(0, 20))
    wc_lda = WordCloud(background_color="white").generate_from_frequencies(topic_words)
    axes[0].imshow(wc_lda, interpolation="bilinear")
    axes[0].axis("off")
    axes[0].set_title("LDA")

    # LSA
    lsa_terms = tfidf_vectorizer.get_feature_names_out()
    lsa_topics = lsa_model.components_
    top_lsa = {lsa_terms[i]: lsa_topics[0][i] for i in lsa_topics[0].argsort()[-20:]}
    wc_lsa = WordCloud(background_color="white").generate_from_frequencies(top_lsa)
    axes[1].imshow(wc_lsa, interpolation="bilinear")
    axes[1].axis("off")
    axes[1].set_title("LSA")

    plt.tight_layout()
    plt.show()


# ----------------- Main Flow ----------------- #
if __name__ == "__main__":
    lda = run_lda()
    lsa = run_lsa()
    run_bert()
    plot_wordclouds(lda, lsa)
    df.to_csv("topic_modeling_results.csv", index=False)