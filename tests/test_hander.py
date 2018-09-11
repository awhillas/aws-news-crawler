import os
import time
import json

# from moto import mock_dynamodb
# from moto.dynamodb2 import dynamodb_backend
from moto import mock_dynamodb2 as mock_dynamodb
from moto.dynamodb2 import dynamodb_backend2 as dynamodb_backend

import src.handler as handler


def test_add_url_http_no_body_in_event():
	# Setup
	url = 'that is not what we expect'
	# Run
	result = handler.add_url_http(url, {})
	# Test results
	assert "Error" in result

def test_add_url_bad_url():
	url = "this in not a URL!"
	result = handler.add_url(url)

	assert 'statusCode' in result
	assert result['statusCode'] == 400
	assert 'body' in result
	assert result['body'] == "Bad 'url' in given JSON?"

# Can't get these to work :(

# @mock_dynamodb
# def test_add_url_known_url():
# 	url = "http://example.com"
# 	event = { "body" : json.dumps({ "url": url }) }
# 	context = {}
# 	table_name = os.environ.get('DYNAMODB_TABLE')
# 	# Create table
# 	dynamodb_backend.create_table(table_name, schema=[ {u'KeyType': u'HASH', u'AttributeName': u'url'} ])
# 	# insert record of URL
# 	timestamp = int(time.time() * 1000)
# 	item = {
# 		'url': { "S": url },
# 		'language': { "S": "xx" },
# 		'addedAt': { "N": timestamp },
# 		'lastCheckedAt': { "N": timestamp },
# 	}
# 	dynamodb_backend.put_item(table_name, item)

# 	result = handler.add_url(event, context)

# 	assert table_name
# 	assert 'statusCode' in result
# 	assert result['statusCode'] == 202
# 	assert 'body' in result
# 	assert result['body'] == "Already tracking {}".format(url)

# @mock_dynamodb
# def test_add_url_unknown_URL():
# 	url = "http://example.com"
# 	event = { "body" : json.dumps({ "url": url }) }
# 	context = {}
# 	table_name = os.environ.get('DYNAMODB_TABLE')
# 	dynamodb_backend.create_table(table_name, schema=[ {u'KeyType': u'HASH', u'AttributeName': u'url'} ])

# 	result = handler.add_url(event, context)
# 	print (result)

# 	assert table_name
# 	assert "Queue" in result
# 	assert "MessageId" in result
# 	assert "MD5OfMessageBody" in result
