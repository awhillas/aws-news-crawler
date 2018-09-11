import json
import logging
import os
import sys
from pprint import pformat
from pprint import pprint as pp

import validators
from url_normalize import url_normalize

from src import feeds, pages, utils

logger = logging.getLogger('HANDLER')


def add_url(url):
	if validators.url(url):
		url = url_normalize(url)
		table = os.environ['DYNAMODB_TABLE']
		if not utils.dynamodb_get(table, url):
			utils.dynamodb_create(table, url, 'xx')  # todo, detect language in RSS or Page
			queue_url = os.environ.get('QUEUE_URL')
			print('>>>>> add_url >>>>> {}'.format(url))
			result = utils.sqs_add(url, queue_url)
			print('>>>>> result >>>>> {}'.format(result))
			return {
				"statusCode": 202,
				"body": str(result),
			}
		else:
			return {
				"statusCode": 202,
				"body": "Already tracking {}".format(url),
			}
	else:
		return {
			"statusCode": 400,
			"body": "Bad 'url' in given JSON?",
		}


def add_url_http(event, context):
	""" Recive a http POST message and forward its contents to an SQS queue.
		Expects JSON in the shape of: {"url": "http://feeds.bbci.co.uk/news/rss.xml"}
	"""
	print(event['body'])
	try:
		data = json.loads(event['body'])
		url = data['url'] if 'url' in data else None
		return add_url(url)
	except:
		return { "Error" : sys.exc_info() }



def add_url_sns(event, context):
	""" Recive an SNS message and stick it on the SQS queue.
		Message body should just be the URL
	"""
	for message in event["Records"]:
		url = url_normalize(message["Sns"]["Message"])
		return add_url(url)


def ingest_rss(event, context):
	""" Triggered by SQS create event.
		'body' should just be the URL
	"""
	topic_arn = os.environ.get('PAGE_ADD_TOPIC')

	for message in event["Records"]:
		# Process the feed, return a list of Page URLs
		info, links = feeds.ingest_rss(message["body"])
		# Add the Pages to PageQueue
		for url in links:
			utils.sns_send(url, topic_arn)

def ingest_aggregator_rss_http(event, context):
	""" Same as ingest_rss except we also add the links to the discover queue
	"""
	try:
		data = json.loads(event['body'])
		url = data['url'] if 'url' in data else None
	except:
		return { "Error" : sys.exc_info() }

	page_topic_arn = os.environ.get('PAGE_ADD_TOPIC')
	discover_topic_arn = os.environ.get('DISCOVER_ADD_TOPIC')

	# Process the feed, return a list of feed metadata and Page URLs
	info, links = feeds.ingest_rss(url)
	# Add the Pages to PageQueue
	for url in links:
		utils.sns_send(url, page_topic_arn)
		utils.sns_send(url, discover_topic_arn)

def discover_feeds(event, context):
	""" Find feeds on the given page and add them to the feeds queue.
		Triggered by SQS create event.
	"""
	topic_arn = os.environ.get('RSS_ADD_TOPIC')
	for message in event["Records"]:
		url = message["body"]
		feed_urls = feeds.discover_feed(url)
		for url in feed_urls:
			utils.sns_send(url, topic_arn)


def ingest_page(event, context):
	""" Triggered by SQS create event.
		'body' should just be the URL.
	"""
	bucket = os.environ.get('PAGE_BUCKET')
	topic_arn = os.environ.get('DISCOVER_ADD_TOPIC')

	for message in event["Records"]:
		url = message["body"]
		html, links = pages.ingest_page(url)
		utils.s3_save(bucket, 'html', url, html)
		# Links for RSS feed discovery
		for url in links:
			utils.sns_send(url, topic_arn)


def process_page(event, context):
	""" Starting point for NLP.
		Triggered by S3 create event
	"""
	for r in event["Records"]:
		if ("s3" in r and
			"object" in r["s3"] and
			"Key" in  r["s3"]["object"] and
			"bucket" in r["s3"] and
			"arn" in r["s3"]["bucker"]):
			pages.process_page(r["s3"]["bucker"]["arn"], r["s3"]["object"]["Key"])
		else:
			print(">>>>>> process_page", "Weird shaped event", pformat(event))
