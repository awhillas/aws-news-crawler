import json
import logging
import os
import sys
from pprint import pformat
from pprint import pprint as pp

import boto3
import validators
from url_normalize import url_normalize

import feeds, pages, utils

logger = logging.getLogger('HANDLER')


def add_url(event, context):
	""" Recive a http POST message and forward its contents to an SQS queue.
		Expects JSON in the shape of: {"url": "http://feeds.bbci.co.uk/news/rss.xml"}
	"""
	try:
		data = json.loads(event['body'])
	except:
		return { "Error" : sys.exc_info() }

	url = data['url'] if 'url' in data else None
	if validators.url(url):
		url = url_normalize(url)
		if not utils.dynamodb_get(url):
			utils.dynamodb_create(url, 'xx')
			print('add_url: {}'.format(url))
			return utils.sqs_send(boto3.client('sqs'), url)
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


def add_url_sns(event, context):
	""" Recive an SNS message and stick it on the SQS queue.
		Message body should just be the URL
	"""
	for message in event["Records"]:
		logger.debug(message)
		url = url_normalize(message["Sns"]["Message"])
		if validators.url(url):
			logger.info('add_url_sns: {}'.format(url))
			return utils.sqs_send(boto3.client('sqs'), url)
		else:
			logger.warning("Invalid URL: {}".format(url))


def poll_url_queue(event, context):
	""" Polls the SQS queue for new RSS feeds and then sends an SNS message
		with each one found for processing.
	"""
	# Get URLs off the queue
	data = utils.sqs_fetch(boto3.client('sqs'))

	# Send the SNS message for each URL in the queue
	sns = boto3.client('sns')
	for d in data:
		utils.sns_send(sns, d)


def ingest_rss(event, context):
	""" Expect an SNS message(s) and process them """
	# Process the feed, return a list of Page URLs
	urls = []
	for message in event["Records"]:
		urls += feeds.ingest_rss(message["Sns"]["Message"])

	# Add the Pages to PageQueue
	sqs = boto3.client('sqs')
	for url in urls:
		utils.sqs_send(sqs, url)


def ingest_page(event, context):
	print(">>>>> INGEST PAGE", pformat(event))
	for message in event["Records"]:
		pages.ingest_page(message["Sns"]["Message"])

def process_page(event, context):
	for r in event["Records"]:
		if ("s3" in r and
			"object" in r["s3"] and
			"Key" in  r["s3"]["object"] and
			"bucket" in r["s3"] and
			"arn" in r["s3"]["bucker"]):
			pages.process_page(r["s3"]["bucker"]["arn"], r["s3"]["object"]["Key"])
		else:
			print(">>>>>> process_page", "Weird shaped event", pformat(event))
