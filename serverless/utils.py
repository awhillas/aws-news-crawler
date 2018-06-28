import json
import logging
import os
import re
import sys
import time
from pprint import pformat
from pprint import pprint as pp

import boto3

S3_SAVE_CHARS = re.compile(r"[^0-9a-zA-Z\!\-\_\.\*\'\(\)]", re.IGNORECASE)

def s3_key_name_sanitiser(key):
	out = re.sub(r'^https?:\/\/', '', key)
	return re.sub(S3_SAVE_CHARS, '-', out)

def sqs_send(client, data):
	""" Expects JSON in the shape of: {"url": "http://feeds.bbci.co.uk/news/rss.xml"}
	"""
	queue_url = os.environ.get('QUEUE_URL')
	response = client.send_message(QueueUrl=queue_url, MessageBody=data)
	return {
		"Queue": queue_url,
		"MessageId": response.get('MessageId'),
		"MD5OfMessageBody": response.get('MD5OfMessageBody')
	}

def sqs_fetch(client):
	""" Gets 10 messages in the quene
		Assumes that 'QUEUE_URL' is set in the env

	Arguments:
		client {AWS SQS Client} -- AWS SQS Client

	Returns:
		[string] -- Returns a list of JSON strings from the message Body
	"""
	queue_url = os.environ.get('QUEUE_URL')
	messages = client.receive_message(QueueUrl=queue_url) #, MaxNumberOfMessages=10)
	data = []
	if 'Messages' in messages:
		print('>>>>> SQS Fetch: ', messages['Messages'])
		for m in messages['Messages']:
			client.delete_message(
				QueueUrl=queue_url,
				ReceiptHandle=m['ReceiptHandle']
			)
			data.append(m['Body'])
	return data

def sns_send(client, data):
	""" Send an SNS topic.
		Assumes 'TOPIC_ARN' is set in the env
	"""
	topic_arn = os.environ.get('TOPIC_ARN')
	print(">>>>>> sns_send ", topic_arn, data)
	response = client.publish(
		TargetArn=topic_arn,
		Message=json.dumps({ 'default': data }),
		MessageStructure='json'
	)
	return response

def dynamodb_get(url):
	""" Get a record from the given table
	"""
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE'))
	# fetch record from the database
	result = table.get_item(
		Key={
			'url':url
		}
	)
	print(">>>>>> dynamodb_get", pformat(result))
	return result['Item'] if 'Item' in result else False

def dynamodb_create(url, lang):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

	timestamp = int(time.time() * 1000)
	item = {
		'id': url,
		'language': lang,
		'addedAt': timestamp,
		'lastCheckedAt': timestamp,
	}

	# write to the database
	table.put_item(Item=item)

	return item
