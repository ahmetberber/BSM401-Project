import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from gensim import corpora
import gensim
import matplotlib.pyplot as plt
from wordcloud import WordCloud

nltk.download('punkt')
nltk.download('punkt_tab')

df = pd.read_csv("cleaned_google_play.csv")
df = df.dropna(subset=["lemmatized_content"])

df["tokenized"] = df["lemmatized_content"].apply(lambda x: word_tokenize(str(x)))

text_data = df["tokenized"].tolist()

dictionary = corpora.Dictionary(text_data)
corpus = [dictionary.doc2bow(text) for text in text_data]
print(f"📌 Kelime sözlüğü boyutu: {len(dictionary)}")

# ---------------------------------------------- #

lda_model = gensim.models.LdaModel(
    corpus, num_topics=5, id2word=dictionary, passes=10
)

for idx, topic in lda_model.print_topics():
    print(f"🔹 Konu {idx + 1}: {topic}\n")

# ---------------------------------------------- #

fig, axes = plt.subplots(1, 5, figsize=(15, 5))

for i, ax in enumerate(axes.flatten()):
    topic_words = dict(lda_model.show_topic(i, 20))  # Her konudaki 20 kelime
    wordcloud = WordCloud(background_color="white").generate_from_frequencies(topic_words)

    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(f"Konu {i+1}")

plt.tight_layout()
plt.show()

# ---------------------------------------------- #

def get_topic(text):
    bow_vector = dictionary.doc2bow(word_tokenize(text))
    topic_distribution = lda_model[bow_vector]
    topic_distribution = sorted(topic_distribution, key=lambda x: x[1], reverse=True)

    if topic_distribution:
        return topic_distribution[0][0]

df["topic"] = df["lemmatized_content"].apply(get_topic)
df.to_csv("lda_result.csv", index=False)
print(df["topic"].value_counts())
