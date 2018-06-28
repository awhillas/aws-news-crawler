import logging
from pprint import pformat
from urllib.parse import urlparse
from urllib.request import urlopen

import feedparser
from feedfinder2 import find_feeds
from url_normalize import url_normalize
from user_agent import generate_user_agent


def ingest_rss(url):
	"""
	Download the RSS feed at the given URL, parse it and return a list of page URLs
	Assume the URL shapes have been validated.
	"""
	feed = feedparser.parse(url)
	return [item['link'] for item in feed['entries']] if 'entries' in feed else []

def ingest_aggregator_rss(url):
	""" Ingest news aggregator which is a feed that points to other sites
		We only want links to other domains ether
		1. directly from the item link itself (digg.com)
		2. Within the content of the link (e.g. Reddit.com). Perhaps have to visit page and scrap link?
	"""
	feed = feedparser.parse(url)

	all_links_are_external = True
	if 'entries' in feed:
		for item in feed['entries']:
			link = urlparse(item['link'])
			if link.netloc == feed.netloc:
				all_links_are_external = False
				break

	if all_links_are_external:
		# Easy just ingest each page linked to
		pass
	else:
		# Special case ;9
		pass

def discover_feed(url):
	""" Find RSS on page if it exists
		TODO: Need to check if it is a link to a page about RSS feeds...?
	"""
	for feed in find_feeds(url):
		ingest_rss(feed)
