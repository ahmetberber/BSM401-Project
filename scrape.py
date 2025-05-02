from app_store_web_scraper import AppStoreEntry
from google_play_scraper import Sort, reviews
import pandas as pd
import time
import praw
from clean import process_dataframe
# from zero_shot import classify_platform_work
from semantic_filter import filter_platformwork_semantically

# Number of reviews to fetch
REVIEW_COUNT = 100

# Fetch reviews from the Apple App Store.
def fetch_app_store_reviews(app_id, country='tr'):
    app_store = AppStoreEntry(app_id=app_id, country=country)
    reviews = app_store.reviews(limit=REVIEW_COUNT)

    return pd.DataFrame([
        {
            "source": "app_store",
            "text": review.content,
            "score": review.rating,
            "timestamp": review.date.strftime('%Y-%m-%d %H:%M:%S'),
            "username": review.user_name
        }
        for review in reviews
    ])

# Fetch reviews from the Google Play Store.
def fetch_play_store_reviews(app_id, lang='tr', country='tr'):
    play_store_reviews, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        count=REVIEW_COUNT,
        sort=Sort.NEWEST
    )

    return pd.DataFrame([
        {
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
            "source": "reddit",
            "text": submission.title + "\n" + submission.selftext,
            "score": submission.score,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(submission.created_utc)),
            "username": submission.author.name if submission.author else "deleted"
        }
        for submission in reddit.subreddit("all").search(query, limit=REVIEW_COUNT, sort='new')
    ])

def main():
    reddit_data = fetch_reddit_posts(
        query="armut OR getir OR trendyol go OR yemeksepeti",
        client_id="Zjvht6OFPqavI2Wd3qiz2g",
        client_secret="HHBB9fgxvut-hRgdEYWlkST08Bq3wQ",
        user_agent="platformwork_project"
    )

    armut_app_store = fetch_app_store_reviews(app_id=1028966163)
    yemeksepeti_app_store = fetch_app_store_reviews(app_id=373034841)
    trendyol_app_store = fetch_app_store_reviews(app_id=6463031298)
    getir_app_store = fetch_app_store_reviews(app_id=995280265)

    armut_play_store = fetch_play_store_reviews("com.armut.armutha")
    yemeksepeti_play_store = fetch_play_store_reviews("com.inovel.app.yemeksepeti")
    trendyol_play_store = fetch_play_store_reviews("com.trendyol.go")
    getir_play_store = fetch_play_store_reviews("com.getir")

    # Combine all data into a single DataFrame
    combined_data = pd.concat([reddit_data, armut_play_store, yemeksepeti_play_store ,trendyol_play_store,
                               getir_play_store, armut_app_store, yemeksepeti_app_store, trendyol_app_store,
                               getir_app_store], ignore_index=True)


    # Clean and process the data
    processed_data = process_dataframe(combined_data)

    # Classify platformwork-related content by applying zero-shot classification
    # It requires a lot of resources and time, so it's commented out.
    # processed_data['platformwork_related'] = processed_data['text'].apply(classify_platform_work)
    # filtered_data = processed_data[processed_data['platformwork_related'] == True]

    # Filter semantically relevant comments
    filtered_data = filter_platformwork_semantically(processed_data)

    # Save the filtered data to a CSV file
    filtered_data.to_csv("comments.csv", index=False, encoding='utf-8')

if __name__ == "__main__":
    main()