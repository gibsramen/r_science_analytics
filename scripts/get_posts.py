import logging
import requests
import time

import praw
import pandas as pd

PUSHSHIFT_URL = "https://api.pushshift.io/reddit/submission/search/"
PARAMS = "&".join([
    "subreddit=science",
    "is_self=False",
    "sort_type=created_utc",
    "limit=10"
])
QUERY_PREFIX = f"{PUSHSHIFT_URL}?{PARAMS}"

logger = logging.getLogger("get_posts")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("scripts/get_posts.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
fh.setFormatter(formatter)
logger.addHandler(fh)


def main(n=100, score_threshold=50):
    with open("keys.txt", "r") as f:
        client_id, client_secret = f.read().splitlines()

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="r_science_analysis"
    )

    posts = []
    current_time = None
    while len(posts) < n:
        data = get_posts(current_time)
        current_time = data[-1]["created_utc"]
        update_post_data(reddit, data)
        posts.extend([x for x in data if x["score"] >= score_threshold])
        logger.info(f"Total posts retrieved: {len(posts)}")
        time.sleep(1)

    df = pd.DataFrame.from_records(posts)
    columns_to_keep = ["score", "author", "created_utc", "id", "permalink",
                       "link_flair_text", "url", "title", "num_comments",
                       "upvote_ratio"]
    df = df.loc[:, columns_to_keep]
    df = df.set_index("id")
    return df


def update_post_data(reddit, posts):
    ids = [f"t3_{y['id']}" for y in posts]
    info = reddit.info(ids)
    for submission, post in zip(info, posts):
        post["score"] = submission.score
        post["upvote_ratio"] = submission.upvote_ratio


def get_posts(before=None):
    """Get list of posts with pushshift."""
    if before is None:
        before = int(time.time())
    query = f"{QUERY_PREFIX}&before={before}"
    result = requests.get(query)
    assert result.status_code == 200
    data = result.json()["data"]
    return data


if __name__ == "__main__":
    df = main(n=10)
    print(df.head())
