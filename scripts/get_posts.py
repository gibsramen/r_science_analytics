import logging
import requests
import time

import click
import praw
import pandas as pd

PUSHSHIFT_URL = "https://api.pushshift.io/reddit/submission/search/"
PARAMS = "&".join([
    "subreddit=science",
    "is_self=False",
    "sort_type=created_utc",
])
QUERY_PREFIX = f"{PUSHSHIFT_URL}?{PARAMS}"


@click.command()
@click.option("--num-posts", default=10, help="Number of posts to retrieve")
@click.option("--score-threshold", default=50, help="Minimum score")
@click.option("--post-limit", default=25, help="Max posts per API call")
@click.option("--log", default="scripts/get_posts.log", help="Log location")
@click.option("--output", help="Output file")
def main(num_posts, score_threshold, post_limit, output, log):
    logger = set_up_logging(log)
    with open("keys.txt", "r") as f:
        client_id, client_secret = f.read().splitlines()

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="r_science_analysis"
    )

    posts = []
    current_time = None
    while len(posts) < num_posts:
        data = get_posts(current_time, post_limit)
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
    df.to_csv(
        output,
        sep="\t",
        index=True
    )


def update_post_data(reddit, posts):
    """Update posts with PRAW info."""
    ids = [f"t3_{y['id']}" for y in posts]
    info = reddit.info(ids)
    for submission, post in zip(info, posts):
        post["score"] = submission.score
        post["upvote_ratio"] = submission.upvote_ratio


def get_posts(before=None, limit=25):
    """Get list of posts with pushshift."""
    if before is None:
        before = int(time.time())
    query = f"{QUERY_PREFIX}&before={before}&limit={limit}"
    result = requests.get(query)
    assert result.status_code == 200
    data = result.json()["data"]
    return data


def set_up_logging(log_location):
    logger = logging.getLogger("get_posts")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_location)
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    main()
