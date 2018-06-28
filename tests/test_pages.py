import cProfile
import io
import os
import pstats

import boto3
import pytest
from lxml.html.diff import htmldiff

import responses
import serverless.pages as pages
from moto import mock_s3
from serverless import utils
from tests.conftest import FEED_URL, PAGE_BUCKET, PAGE_FILE, PAGE_URL


@mock_s3
@responses.activate
def test_ingest_page(urls):
	# We need to create the bucket since this is all in Moto's 'virtual' AWS account
	s3 = boto3.resource('s3')
	s3.create_bucket(Bucket=PAGE_BUCKET, CreateBucketConfiguration={'LocationConstraint':'eu-west-1'})

	# Run it!
	pages.ingest_page(PAGE_URL)

	# Test results
	safe_key = utils.s3_key_name_sanitiser(PAGE_URL)
	html = s3.Object(PAGE_BUCKET, 'raw/{}'.format(safe_key)).get()['Body'].read().decode("utf-8")
	with open(PAGE_FILE) as f:
		assert htmldiff(html, f.read())
	content = s3.Object(PAGE_BUCKET, 'content/{}'.format(safe_key)).get()['Body'].read().decode("utf-8")

	assert content == 'TODO!'

def test_extract_content():
	pass

def test_process_page():
	pass


# Performace tuning...

# @mock_s3
# @responses.activate
# def test_ingest_page_preformance(urls):
# 	s3 = boto3.resource('s3')
# 	s3.create_bucket(Bucket=PAGE_BUCKET)

# 	pr = cProfile.Profile()
# 	pr.enable()
# 	# what we're testing -----------
# 	pages.ingest_page(PAGE_URL)
# 	# ------------------------------
# 	pr.disable()
# 	s = io.StringIO()
# 	sortby = 'cumulative'
# 	ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
# 	ps.print_stats(.1)
# 	print(s.getvalue())
# 	assert False
