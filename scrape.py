from app_store_web_scraper import AppStoreEntry
from google_play_scraper import Sort, reviews
import pandas as pd
import time
import praw
from clean import process_dataframe
from semantic_filter import filter_platformwork_semantically
import csv

# Number of reviews to fetch
REVIEW_COUNT = 500

# Fetch reviews from the Apple App Store.
def fetch_app_store_reviews(app, app_id, country='tr'):
    app_store = AppStoreEntry(app_id=app_id, country=country)
    reviews = app_store.reviews(limit=REVIEW_COUNT)

    return pd.DataFrame([
        {
            "app": app,
            "source": "app_store",
            "text": review.content,
            "score": review.rating,
            "timestamp": review.date.strftime('%Y-%m-%d %H:%M:%S'),
            "username": review.user_name
        }
        for review in reviews
    ])

# Fetch reviews from the Google Play Store.
def fetch_play_store_reviews(app, app_id, lang='tr', country='tr'):
    play_store_reviews, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        count=REVIEW_COUNT,
        sort=Sort.NEWEST
    )

    return pd.DataFrame([
        {
            "app": app,
            "source": "play_store",
            "text": review['content'],
            "score": review['score'],
            "timestamp": review['at'].strftime('%Y-%m-%d %H:%M:%S'),
            "username": review['userName']
        }
        for review in play_store_reviews
    ])

# Fetch posts from Reddit based on a search query.
def fetch_reddit_posts(query, client_id, client_secret, user_agent):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    return pd.DataFrame([
        {
            "app": "reddit",
            "source": "reddit",
            "text": submission.title + "\n" + submission.selftext,
            "score": submission.score,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(submission.created_utc)),
            "username": submission.author.name if submission.author else "deleted"
        }
        for submission in reddit.subreddit("all").search(query, limit=REVIEW_COUNT, sort='new')
    ])

def fetch_data_from_platforms():
    # Fetch data from tr platforms
    reddit_tr_data = fetch_reddit_posts(
        query="armut OR getir OR trendyol OR yemeksepeti",
        client_id="Zjvht6OFPqavI2Wd3qiz2g",
        client_secret="HHBB9fgxvut-hRgdEYWlkST08Bq3wQ",
        user_agent="platformwork_project"
    )

    armut_app_store = fetch_app_store_reviews("armut", app_id=1028966163)
    yemeksepeti_app_store = fetch_app_store_reviews("yemeksepeti", app_id=373034841)
    trendyol_app_store = fetch_app_store_reviews("trendyol", app_id=6463031298)
    getir_app_store = fetch_app_store_reviews("getir", app_id=995280265)

    armut_play_store = fetch_play_store_reviews("armut", "com.armut.armutha")
    yemeksepeti_play_store = fetch_play_store_reviews("yemeksepeti", "com.inovel.app.yemeksepeti")
    trendyol_play_store = fetch_play_store_reviews("trendyol", "com.trendyol.go")
    getir_play_store = fetch_play_store_reviews("getir", "com.getir")

    combined_tr_data = pd.concat([reddit_tr_data, armut_play_store, yemeksepeti_play_store ,trendyol_play_store,
                               getir_play_store, armut_app_store, yemeksepeti_app_store, trendyol_app_store,
                               getir_app_store], ignore_index=True)

    # Fetch data from us platforms
    reddit_us_data = fetch_reddit_posts(
        query="flexjobs OR toptal OR deel",
        client_id="Zjvht6OFPqavI2Wd3qiz2g",
        client_secret="HHBB9fgxvut-hRgdEYWlkST08Bq3wQ",
        user_agent="platformwork_project"
    )

    flexjobs_app_store = fetch_app_store_reviews("flexjobs", app_id=800818884, country='us')
    toptal_app_store = fetch_app_store_reviews("toptal", app_id=1378985638, country='us')
    deel_app_store = fetch_app_store_reviews("deel", app_id=6478083155, country='us')

    flexjob_play_store = fetch_play_store_reviews("flexjobs", "com.bold.flexjobs", lang='en', country='us')
    toptal_play_store = fetch_play_store_reviews("toptal", "com.toptal.talent", lang='en', country='us')
    deel_play_store = fetch_play_store_reviews("deel", "com.deel.app", lang='en', country='us')

    combined_us_data = pd.concat([reddit_us_data, flexjob_play_store, toptal_play_store, deel_play_store,
                               flexjobs_app_store, toptal_app_store, deel_app_store], ignore_index=True)


    # Clean and process the data
    processed_tr_data = process_dataframe(combined_tr_data, lang='tr')
    processed_us_data = process_dataframe(combined_us_data, lang='en')
    processed_tr_data.to_csv("tr_data.csv", index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)
    processed_us_data.to_csv("us_data.csv", index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)

def main():
    # Fetch data from platforms
    fetch_data_from_platforms()

    # Filter semantically relevant comments
    processed_tr_data = pd.read_csv("tr_data.csv")
    filtered_tr_data = filter_platformwork_semantically(processed_tr_data, lang='tr')
    processed_us_data = pd.read_csv("us_data.csv")
    filtered_us_data = filter_platformwork_semantically(processed_us_data, lang='en')

    # # Save the filtered data to a CSV file
    filtered_tr_data.to_csv("tr_processed_data.csv", index=False, encoding='utf-8')
    filtered_us_data.to_csv("us_processed_data.csv", index=False, encoding='utf-8')
    print("Filtered data saved to tr_processed_data.csv and us_processed_data.csv")

if __name__ == "__main__":
    main()