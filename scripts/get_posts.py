import requests
import time

import click
import praw
import pandas as pd

from src.util import set_up_logging

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
@click.option("--log",
              default="scripts/log/get_posts.log",
              help="Log location")
@click.option("--output", help="Output file")
def main(num_posts, score_threshold, post_limit, output, log):
    logger = set_up_logging(log)
    param_log = " ".join([
        f"num_posts: {num_posts}",
        f"score_threshold: {score_threshold}",
        f"post_limit: {post_limit}",
        f"log_file: {log}",
        f"output: {output}\n"
    ])
    logger.info(param_log)
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
        current_time = data[-1]["created_utc"]  # get posts older than oldest

        # For some reason pushshift doesn't properly retrieve submission
        # scores so I'm going to get those using PRAW.
        update_post_data(reddit, data)
        posts.extend([x for x in data if x["score"] >= score_threshold])
        logger.info(f"Total posts retrieved: {len(posts)}")
        time.sleep(1)  # sleep to respect pushshift rate limit

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
    """Get chronological list of posts with pushshift."""
    if before is None:
        before = int(time.time())
    query = f"{QUERY_PREFIX}&before={before}&limit={limit}"
    result = requests.get(query)
    assert result.status_code == 200
    data = result.json()["data"]
    return data


if __name__ == "__main__":
    main()
