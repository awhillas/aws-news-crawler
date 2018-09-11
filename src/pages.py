import logging
import os
from pprint import pprint as pp
from urllib.parse import urlparse

import boto3
import requests
import src.utils as utils
import validators
from bs4 import BeautifulSoup
from feedfinder2 import find_feeds
import bs4 as BeautifulSoup

logger = logging.getLogger('HANDLER')


def extract_content(html):
	""" TODO: Auto content detection
	"""
	return html

def ingest_page(url):
	""" TODO: get date of article so we can cluster content by day
	"""
	print(">>>>>>> ingest_page", url)

	# Get main content

	resp = requests.get(url)
	soup = BeautifulSoup.BeautifulSoup(resp.content, 'html5lib')

	# Remove nodes that have text content but do not contribute to the content we're interested in.
	# SVG is just bulky and obviously not relevant.
	for tag in ['script', 'noscript', 'style', 'svg', 'figcaption']:
		for s in soup(tag):
			s.extract()

	html = soup.prettify()
	# html = extract_content(html)

	# Get links to spider

	links = set()
	this_domain = urlparse(url).netloc
	for link in soup.find_all('a', href=True):
		href = link.get('href')
		if validators.url(href):
			# We're only interested in domains for now, assume 1 RSS feed per domain.
			domain = urlparse(href).netloc
			if not domain == this_domain and not any((domain in href for domain in ['facebook.com', 'twitter.com', 'youtube.com', 'instagram.com'])):
				links.add("http://{}".format(domain))

	return html, links


def process_page(bucket_arn, file_key):
	""" Starting point for NLP
		- Content extraction?
		- language detection
		- Author detection
	"""
	logger.debug(">>>>> process_page(bucket_arn={}, file_key={})".format(bucket_arn, file_key))
