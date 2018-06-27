import os

import boto3
import requests
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
from dragnet import extract_content
from feedfinder2 import find_feeds


def ingest_page(url):
	""" TODO: Download the page and detect content
	"""
	bucket = os.environ.get('PAGE_BUCKET')

	print(">>>>>>> ingest_page", url)

	# This thanks to https://stackoverflow.com/a/22583436/196732
	resp = requests.get(url)
	s3 = boto3.resource('s3')
	http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
	html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
	encoding = html_encoding or http_encoding

	print(">>>>>>", encoding, resp.text[:50])

	# Parse the dirty HTML

	soup = BeautifulSoup(resp.content, from_encoding=encoding)
	s3.Bucket(bucket).put_object(Key="raw/{}".format(url), Body=soup.prettify())
	clean_html = str(soup)

	# Get links to spider

	for link in soup.find_all('a', href=True):
		# TODO: send links to feed discovery
		print(link['href'])

	# Get main content

	content = extract_content(clean_html)
	s3.Bucket(bucket).put_object(Key="content/{}".format(url), Body=content)

def process_page(bucket_arn, file_key):
	""" Starting point for NLP """
	pass
