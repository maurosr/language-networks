import itertools
from collections import Counter
import networkx as nx
import nltk
from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2, OAuth2Session

from Scrapper import Scraper
from credentials import CLIENT_ID, CLIENT_SECRET


class TwitterScraper(Scraper):
    BASE_URL = 'https://api.twitter.com'
    AUTH_URL = f'{BASE_URL}/oauth2/token'
    SEARCH_URL = f'{BASE_URL}/1.1/search/tweets.json'

    # OAUTH 2.0
    CLIENT = BackendApplicationClient(client_id=CLIENT_ID)
    OAUTH = OAuth2Session(client=CLIENT)

    nltk.download('punkt')

    def __init__(self):
        super().__init__()
        self._network = nx.Graph()

    def scrape(self, lang='es'):
        token = TwitterScraper._authenticate()
        auth = OAuth2(CLIENT_ID, TwitterScraper.CLIENT, token=token)
        params = {'q': 'a', 'lang': lang, 'count': 100}

        r = requests.get(TwitterScraper.SEARCH_URL, params=params, auth=auth)
        c = Counter()
        for text in TwitterScraper._get_tweets_text(r):
            for sentence in nltk.sent_tokenize(text, language='spanish'):
                for word1, word2 in itertools.product(nltk.word_tokenize(sentence, language='spanish'), repeat=2):
                    word1, word2 = min(word1, word2), max(word1, word2)
                    c[(word1, word2)] += 1

        for (word1, word2), weight in c.items():
            nx.add_path(self._network, [word1, word2], weight=weight)
        return self._network

    @staticmethod
    def _authenticate():
        return TwitterScraper.OAUTH.fetch_token(token_url=TwitterScraper.AUTH_URL, client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET)

    @staticmethod
    def _get_tweets_text(r):
        jr = r.json()
        if 'errors' in jr:
            print(jr['errors'])
            exit(1)

        for tweet in jr['statuses']:
            yield tweet['text']
