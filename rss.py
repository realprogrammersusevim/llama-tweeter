import json
from datetime import datetime
from html import unescape
from urllib.request import Request, urlopen

import dateparser
import xmltodict
from bs4 import BeautifulSoup as soup


def save():
    with open("feeds.json") as j:
        feeds = json.load(j)

    for feed in feeds["world_news"]:
        result = Request("https://" + feed, headers={"User-Agent": "Mozilla/5.0"})
        text = urlopen(result).read()

        with open(feed, "xb") as f:
            f.write(text)


def parse_xml(text, source) -> list[dict]:
    items: list[dict] = []

    for item in xmltodict.parse(text)["rss"]["channel"]["item"]:
        try:
            items.append(
                {
                    "source": source,
                    "title": unescape(item["title"]),
                    # Format: Sun, 06 Aug 2023 14:05:17 EDT
                    "pubdate": dateparser.parse(item["pubDate"]),
                    "description": unescape(item["description"]),
                    "content": "\n".join(
                        unescape(soup(item["content:encoded"], "lxml").get_text())
                    ),
                }
            )
        except:
            continue

    return items


def get_feeds():
    with open("feeds.json") as j:
        feeds = json.load(j)

    xml = []

    for feed in feeds["world_news"]:
        result = Request(feed["url"], headers={"User-Agent": "Mozilla/5.0"})
        text = urlopen(result).read()
        xml.append({"name": feed["name"], "text": text})

    return xml


def past_day(items: list[dict]) -> list[dict]:
    todays = []

    for i in items:
        if i["pubdate"].date() == datetime.now().date():
            todays.append(i)

    return todays


if __name__ == "__main__":
    with open("save.txt", "rb") as f:
        print(past_day(parse_xml(f, "Fox News")))
