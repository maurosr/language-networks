import re
from collections import Counter
from multiprocessing.pool import ThreadPool
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

    def __init__(self, user_ids, base_params):
        super().__init__()
        self._tokenizer = RegexpTokenizer(r'\w+')
        self._base_params = base_params
        self._user_ids = user_ids
        self._auth = OAuth2(CLIENT_ID, TwitterScraper.CLIENT, token=TwitterScraper._authenticate())
        self._stop_words = stopwords.words('spanish')

    def scrape(self):
        network = nx.Graph()
        thread_pool = ThreadPool(processes=1)

        words = []

        responses = thread_pool.imap(self._make_request, self._user_ids)
        for user_id, response in zip(self._user_ids, responses):
            c = Counter()
            for text in TwitterScraper._get_tweets_text(response):
                for sentence in nltk.sent_tokenize(text, language='spanish'):
                    for word in self._tokenize(sentence):
                        words.append(word)
                        c[(user_id, word)] += 1

            for user_id_word_pair, weight in c.items():
                nx.add_path(network, user_id_word_pair, weight=weight)

        thread_pool.close()
        thread_pool.join()

        return network

    def _make_request(self, user_id):
        # TODO: pagination
        params = dict(self._base_params)
        params['q'] = 'from:{}'.format(user_id.replace('@', ''))
        return requests.get(TwitterScraper.SEARCH_URL, params=params, auth=self._auth)

    @staticmethod
    def _authenticate():
        return TwitterScraper.OAUTH.fetch_token(token_url=TwitterScraper.AUTH_URL, client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET)

    def _tokenize(self, text):
        urls = re.findall(r"http\S+", text)
        with_no_urls = re.sub(r"http\S+", "", text)
        words = self._tokenizer.tokenize(with_no_urls)
        return [w.upper() for w in words if w not in self._stop_words] + urls


    @staticmethod
    def _get_tweets_text(r):
        jr = r.json()
        if 'errors' in jr:
            print('Hubo un error:')
            print(r.request.__dict__)
            print(jr['errors'])
            exit(1)

        for tweet in jr['statuses']:
            yield tweet['text']

