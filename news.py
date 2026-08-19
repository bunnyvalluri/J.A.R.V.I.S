import feedparser
import urllib.parse
from ui import print_info, print_status, PRIMARY, SUCCESS, MUTED

NEWS_FEEDS = {
    "top": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "tech": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "india": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
}

def fetch_headlines(category="top", limit=5):
    """
    Fetch live news headlines from RSS feeds.
    Returns a list of dicts with 'title' and 'link'.
    """
    feed_url = NEWS_FEEDS.get(category, NEWS_FEEDS["top"])
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "Headline unavailable")
            # Clean title
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
            articles.append({
                "title": title.strip(),
                "link": entry.get("link", "")
            })
        return articles
    except Exception as e:
        print_info(f"Failed to fetch RSS news: {e}")
        return []

def speak_news(speaker_func=None, category="top", limit=4):
    """
    Fetch and announce top news headlines.
    """
    articles = fetch_headlines(category=category, limit=limit)
    if not articles:
        msg = "I am unable to retrieve today's news headlines at the moment, Sir."
        if speaker_func:
            speaker_func(msg)
        return msg, []

    intro = f"Here are today's top {len(articles)} headlines, Sir:"
    if speaker_func:
        speaker_func(intro)

    for i, art in enumerate(articles, 1):
        headline_text = f"Headline {i}: {art['title']}"
        print_status("NEWS", f"#{i}: {art['title']}", PRIMARY)
        if speaker_func:
            speaker_func(art['title'])

    outro = "Those were the top headlines."
    if speaker_func:
        speaker_func(outro)

    return intro, articles

def getNewsUrl():
    return "https://news.google.com"

if __name__ == '__main__':
    arts = fetch_headlines()
    for i, a in enumerate(arts, 1):
        print(f"{i}. {a['title']}")
