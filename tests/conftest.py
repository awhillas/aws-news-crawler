import os

import pytest
import responses
import boto3
from moto import mock_s3

import src.pages as pages


PAGE_URL = 'http://example.com'
PAGE_FILE = 'tests/data/nytimes.com.html'
FEED_URL = PAGE_URL + '/nytimes.rss.xml'
FEED_FILE = 'tests/data/nytimes.rss.xml'
PAGE_BUCKET = os.environ.get('PAGE_BUCKET')


@pytest.fixture(params=[{PAGE_URL: PAGE_FILE, FEED_URL: FEED_FILE}])
def urls(request):
	url_map = request.param
	# Mock the requests
	for url, local_file in url_map.items():
		with open(local_file) as f:
			print("Mocking", url, " >>>> ", local_file)
			responses.add(responses.GET, url, body=f.read())
	return urls



