from serverless.feeds import ingest_rss, discover_feed


def test_ingest_rss():
	with open('tests/digg.rss') as f:
		pages = ingest_rss(f.read())
	assert pages[0] == 'https://www.vanityfair.com/style/2018/06/nigeria-world-cup-jersey?mbid=synd_digg'
	assert pages[-1] == 'http://digg.com/channel/donaldtrump'

def test_discover_feed():
	with open('tests/digg.com.html') as f:
		pages = discover_feed(f.read())


