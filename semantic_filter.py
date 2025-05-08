import pandas as pd
from sentence_transformers import SentenceTransformer, util

def filter_platformwork_semantically(df, lang="tr", threshold=0.4):
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # Hedef cümleleri dosyadan oku ve dile göre filtrele
    target_df = pd.read_csv("platformwork_targets.csv")
    target_sentences = target_df[target_df["lang"] == lang]["text"].tolist()

    # Embedding hesapla
    target_embeddings = model.encode(target_sentences, convert_to_tensor=True)
    mean_target = target_embeddings.mean(dim=0)

    df = df[df["text"].notnull()]
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""]

    comment_embeddings = model.encode(df["text"].tolist(), convert_to_tensor=True)
    cosine_scores = util.cos_sim(comment_embeddings, mean_target).squeeze()
    df["similarity"] = cosine_scores.cpu().numpy()

    return df[df["similarity"] >= threshold].sort_values(by="similarity", ascending=False)
