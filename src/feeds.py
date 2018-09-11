from datetime import datetime
import logging
from pprint import pformat
from urllib.parse import urlparse
from urllib.request import urlopen

from dateutil.parser import parse
import feedparser
import pytz

from feedfinder2 import find_feeds
from url_normalize import url_normalize
from user_agent import generate_user_agent


def ingest_rss(url):
	"""
	Download the RSS feed at the given URL, parse it and return a list of page URLs
	Assume the URL shapes have been validated.
	"""
	feed = feedparser.parse(url)
	feed_details = {
		'title': feed['feed']['title'] if 'title' in feed['feed'] else '',
		'language': feed['feed']['language'] if 'language' in feed['feed'] else 'xx',
		'publish_date': parse(feed['feed']['published']) if 'published' in feed['feed'] else parse(feed['feed']['updated']) if 'updated' in feed['feed'] else datetime.now(tz=pytz.utc)
	}
	links = [item['link'] for item in feed['entries']] if 'entries' in feed else []
	return feed_details, links


def discover_feed(url):
	""" Find RSS on page if it exists
		TODO: Need to check if it is a link to a page about RSS feeds...?
	"""
	return [feed for feed in find_feeds(url) if 'comments' not in feed]

