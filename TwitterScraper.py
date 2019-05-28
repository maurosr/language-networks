import re
from collections import Counter
from nltk.tokenize import RegexpTokenizer


import networkx as nx
import nltk
from oauthlib.oauth2 import BackendApplicationClient
import requests
from requests_oauthlib import OAuth2, OAuth2Session

from Scrapper import Scraper
from credentials import CLIENT_ID, CLIENT_SECRET
from nltk.corpus import stopwords


class TwitterScraper(Scraper):
    BASE_URL = 'https://api.twitter.com'
    AUTH_URL = f'{BASE_URL}/oauth2/token'
    SEARCH_URL = f'{BASE_URL}/1.1/search/tweets.json'

    # OAUTH 2.0
    CLIENT = BackendApplicationClient(client_id=CLIENT_ID)
    OAUTH = OAuth2Session(client=CLIENT)

    nltk.download('punkt')
    nltk.download('stopwords')

    def __init__(self, user_ids):
        super().__init__()
        self._tokenizer = RegexpTokenizer(r'\w+')
        self._user_ids = user_ids
        self._auth = OAuth2(CLIENT_ID, TwitterScraper.CLIENT, token=TwitterScraper._authenticate())
        self._stop_words = stopwords.words('spanish')

    def scrape(self):
        network = nx.Graph()
        words = []

        for user_id in self._user_ids:
            c = Counter()
            for text in self._get_tweets(user_id):
                for sentence in nltk.sent_tokenize(text, language='spanish'):
                    for word in self._tokenize(sentence):
                        words.append(word)
                        c[(user_id, word)] += 1

            for user_id_word_pair, weight in c.items():
                nx.add_path(network, user_id_word_pair, weight=weight)

        return network

    @staticmethod
    def _authenticate():
        return TwitterScraper.OAUTH.fetch_token(token_url=TwitterScraper.AUTH_URL, client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET)

    def _tokenize(self, text):
        # Let's leave urls out for now
        # urls = re.findall(r"http\S+", text)
        with_no_urls = re.sub(r"http\S+", "", text)
        words = self._tokenizer.tokenize(with_no_urls)
        return [w.upper() for w in words if w.lower() not in self._stop_words and not re.match(r"^\d+$", w)]  # + urls

    def _get_tweets(self, user_id):
        res = []
        url = TwitterScraper.SEARCH_URL
        params = {
            'q': 'from:{}'.format(user_id.replace('@', '')),
            'tweet_mode': 'extended'
        }

        eot = False
        while not eot:
            tweets, next_results_url_tail = self._make_request_and_parse(url, params)
            res += tweets
            eot = next_results_url_tail is None or next_results_url_tail == ''
            url = TwitterScraper.SEARCH_URL + next_results_url_tail + '&tweet_mode=extended'
            params = None

        return res

    def _make_request_and_parse(self, url, params=None):
        tweets = []

        r = requests.get(url, params=params, auth=self._auth)
        jr = r.json()
        if 'errors' in jr:
            raise RuntimeError(jr['errors'])

        next_results_url_tail = jr['search_metadata'].get('next_results', '')

        for tweet in jr['statuses']:
            tweets.append(tweet['full_text'])

        return tweets, next_results_url_tail
