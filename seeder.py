import sys
import requests
import json

GOOGLE_NEWS_URL = "https://news.google.com/news/rss/search/section/q/{query}"
ADD_FEED_URL = "https://89ka99oawb.execute-api.eu-west-1.amazonaws.com/dev/add_rss"



def main(url):
	payload = { 'url': url }
	r = requests.post(ADD_FEED_URL, data=json.dumps(payload))
	print(r.status_code)

if __name__ == "__main__":
	main(sys.argv[1:])
