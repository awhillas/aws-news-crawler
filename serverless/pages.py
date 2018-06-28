import os
from pprint import pprint as pp
from urllib.parse import urlparse

import boto3
import lxml.html
import requests
import validators
from bs4.dammit import EncodingDetector
from feedfinder2 import find_feeds

import utils

def extract_content(html):
	return 'TODO!'


def ingest_page(url):
	""" TODO: Download the page and detect content
	"""
	s3 = boto3.resource('s3')
	bucket = os.environ.get('PAGE_BUCKET')

	print(">>>>>>> ingest_page", url)

	# This thanks to https://stackoverflow.com/a/22583436/196732
	resp = requests.get(url)
	http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
	html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
	encoding = html_encoding or http_encoding

	print(">>>>>> ENCODING:", encoding, resp.text[:100])

	# Parse the dirty HTML, clean and save it to s3

	dom =  lxml.html.fromstring(resp.content)
	clean_html = lxml.html.tostring(dom)
	safe_key = utils.s3_key_name_sanitiser(url)
	s3.Bucket(bucket).put_object(Key="raw/{}".format(safe_key), Body=clean_html)


	# Get links to spider

	links = set()
	this_domain = urlparse(url).netloc

	for href in dom.xpath('//a/@href'):  #soup.find_all('a', href=True):
		# TODO: send links to feed discovery
		if validators.url(href):
			domain = urlparse(href).netloc
			# if (not any([href.lower().endswith("." + ext) for ext in ['jpeg', 'jpg', 'gif', 'png', 'js', 'css']])
			# 	and not any((domain in href for domain in ['facebook.com', 'twitter.com']))
			# 	):
			if not domain == this_domain and not any((domain in href for domain in ['facebook.com', 'twitter.com'])):
				links.add(domain)
	pp(links)

	# Get main content

	content = extract_content(clean_html)
	s3.Bucket(bucket).put_object(Key="content/{}".format(safe_key), Body=content)


def process_page(bucket_arn, file_key):
	""" Starting point for NLP """
	pass
