import os

from dotenv import load_dotenv

import twitter

# Load all our keys
load_dotenv()
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

# Check that all the keys are accounted for
if (
    not consumer_key
    or not consumer_secret
    or not access_token
    or not access_token_secret
):
    raise Exception("Could not find keys")

tweet = {
    "text": 'Did you know the "Hello World!" example programmed was first used in the book "The C Programming Language"?'
}

resp = twitter.post_tweet(
    payload=tweet,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)
