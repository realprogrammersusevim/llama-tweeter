import os
import random

from dotenv import load_dotenv

import llama
import rss
import twitter

# Load all our keys
load_dotenv()
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
model_path = os.environ.get("LLAMA_PATH")

# Check that all the keys are accounted for
if (
    not consumer_key
    or not consumer_secret
    or not access_token
    or not access_token_secret
):
    raise ValueError("Could not find keys")

# twitter.get_oath(consumer_key, consumer_secret)
# input()

# with open("save.txt", "rb") as f:
#     news = rss.parse_xml(f, "Fox News")

feeds = rss.get_feeds()
news = []

for i in feeds:
    news.extend(rss.past_day(rss.parse_xml(i["text"], i["name"])))

descriptions = [f'{i["description"]} (Source: {i["source"]})' for i in news]
random.shuffle(descriptions)
descriptions = descriptions[0:10]
summary = llama.summarize_text("\n".join(descriptions), model_path)

tweet = {"text": summary}

resp = twitter.post_tweet(
    payload=tweet,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)
