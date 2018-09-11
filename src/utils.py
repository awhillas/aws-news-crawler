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
	""" Make key name safe for S3
		see: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#object-key-guidelines
	"""
	out = re.sub(r'^https?:\/\/', '', key)
	return re.sub(S3_SAVE_CHARS, '-', out)


def s3_save(bucket, prefix, key, content):
	s3 = boto3.resource('s3')
	safe_key = s3_key_name_sanitiser(key)
	print(">>>>> s3_save >>>>> BUCKEY:{} KEY:{}/{}".format(bucket, prefix, safe_key))
	s3.Bucket(bucket).put_object(Key="{}/{}".format(prefix, safe_key), Body=content)


def sqs_add(data, queue_url):
	""" data can any string, i.e. a URL or JSON
	"""
	sqs = boto3.resource('sqs')
	queue = sqs.Queue(queue_url)
	return queue.send_message(MessageBody=data)

def sns_send(data, topic_arn):
	""" Send data to a SNS topics
	"""
	sns = boto3.resource('sns')
	topic = sns.Topic(topic_arn)
	return topic.publish(Message=data)

def dynamodb_get(table_name, url):
	""" Get a record from the given table
	"""
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(table_name)
	# fetch record from the database
	result = table.get_item(Key={ 'url': url })
	return result['Item'] if 'Item' in result else False


def dynamodb_create(table_name, url, lang):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(table_name)

	timestamp = int(time.time() * 1000)
	item = {
		'url': url,
		'language': lang,
		'addedAt': timestamp,
		'lastCheckedAt': timestamp,
	}
	# write to the database
	table.put_item(Item=item)

	return item
