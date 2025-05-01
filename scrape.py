from app_store_scraper import AppStore
from google_play_scraper import Sort, reviews
import pandas as pd
import time
import praw
from clean import process_dataframe
from zero_shot import classify_platform_work
from semantic_filter import filter_platformwork_semantically

# Number of reviews to fetch
REVIEW_COUNT = 100

# Fetch reviews from the Apple App Store.
def fetch_app_store_reviews(app_id, country, app_name):
    app_store = AppStore(country=country, app_name=app_name, app_id=app_id)
    app_store.review(how_many=REVIEW_COUNT)

    return pd.DataFrame([
        {
            "source": "app_store",
            "text": review['content'],
            "score": review['rating'],
            "timestamp": review['date'].strftime('%Y-%m-%d %H:%M:%S'),
            "username": review['userName']
        }
        for review in app_store.reviews
    ])

# Fetch reviews from the Google Play Store.
def fetch_play_store_reviews(app_id, lang='tr', country='tr', sort=Sort.NEWEST):
    play_store_reviews, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        count=REVIEW_COUNT,
        sort=sort
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
        query="platform işi deneyimi",
        client_id="Zjvht6OFPqavI2Wd3qiz2g",
        client_secret="HHBB9fgxvut-hRgdEYWlkST08Bq3wQ",
        user_agent="platformwork_project"
    )

    # app_store_data = fetch_app_store_reviews(
    #     app_id=6463031298,
    #     country="tr",
    #     app_name="trendyol-go"
    # )

    play_store_data = fetch_play_store_reviews("com.armut.armutha")

    # Combine all data into a single DataFrame
    combined_data = pd.concat([reddit_data, play_store_data], ignore_index=True)

    # Clean and process the data
    processed_data = process_dataframe(combined_data)
    processed_data.to_csv("processed_comments.csv", index=False, encoding='utf-8')

    # Classify platformwork-related content by applying zero-shot classification
    # It requires a lot of resources and time, so it's commented out.
    # processed_data['platformwork_related'] = processed_data['text'].apply(classify_platform_work)
    # filtered_data = processed_data[processed_data['platformwork_related'] == True]

    # Filter semantically relevant comments
    filtered_data = filter_platformwork_semantically(processed_data, top_k=300)

    # Save the filtered data to a CSV file
    filtered_data.to_csv("comments.csv", index=False, encoding='utf-8')

if __name__ == "__main__":
    main()