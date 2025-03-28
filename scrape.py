from app_store_scraper import AppStore
from google_play_scraper import Sort, reviews
import pandas as pd

count = 100

def fetch_app_store_reviews(app_id, country, app_name):
    app_store = AppStore(
        country=country,
        app_name=app_name,
        app_id=app_id,
    )
    app_store.review(how_many=count)
    return pd.DataFrame(app_store.reviews)

def fetch_play_store_reviews(app_id, lang='tr', country='tr', sort=Sort.NEWEST):
    play_store_reviews, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        count=count,
        sort=sort
    )
    df_play_store = pd.DataFrame(play_store_reviews)
    return df_play_store[['content', 'score', 'at', 'userName']]

def save_reviews_to_csv(df, filename):
    df.to_csv(filename, index=False, encoding='utf-8')

if __name__ == "__main__":
    app_store_reviews = fetch_app_store_reviews(
        app_id=1028966163,
        country="tr",
        app_name="Armut - Hizmet Piş, Ağzıma Düş".encode('utf-8')
    )
    play_store_reviews = fetch_play_store_reviews("com.armut.armutha")

    save_reviews_to_csv(app_store_reviews, "app_store.csv")
    save_reviews_to_csv(play_store_reviews, "google_play.csv")