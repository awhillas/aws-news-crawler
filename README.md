![A smoking dog](newshound.jpg)

# NewHound: AWS Lambda based Web Crawler

A Serverless.js project that sets up lambda functions, SQS queues and communicates between them all via SNS. Pages are stored in an S3 bucket for cheap, scalable storage and for later processinf. This infrastructure allows unlimited scalability.

Content extraction is performed algorithmlically and content is grouped by langauge (possibly region?).

## Setup

Setup requires [npm](https://www.npmjs.com/get-npm) installed and [pipenv](https://pipenv.readthedocs.io/en/latest/) install.

	npm install
	pipenv install

## Deployment

	sls deploy

## Testing

locally:

	pipenv shell
	python -m pytest

remotely try (replacing the 'kqoorz3y6h' with real hash):

	curl -X POST -d '{ "url": "http://feeds.bbci.co.uk/news/rss.xml" }' https://kqoorz3y6h.execute-api.eu-west-1.amazonaws.com/dev/add_rss


## TODOs

- Ingest sitemap.xml files taken from the root or the robots.txt
- Near-duplicates detection via shingling.
