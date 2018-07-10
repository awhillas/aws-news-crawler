from src.feeds import ingest_rss, discover_feed

from tests.conftest import PAGE_FILE, FEED_FILE


def test_ingest_rss():
	with open(FEED_FILE) as f:
		pages = ingest_rss(f.read())
	assert pages[0] == 'https://www.nytimes.com/2018/06/27/us/politics/anthony-kennedy-retire-supreme-court.html?partner=rss&emc=rss'
	assert pages[-1] == 'https://www.nytimes.com/2018/06/26/science/spiders-ballooning-wind.html?partner=rss&emc=rss'

def test_ingest_aggregator_rss():
	pass

def test_discover_feed():
	with open(PAGE_FILE) as f:
		pages = discover_feed(f.read())


