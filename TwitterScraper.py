import networkx as nx
import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from Scrapper import Scraper
from credentials import CLIENT_ID, CLIENT_SECRET


class TwitterScraper(Scraper):
    BASE_URL = 'https://api.twitter.com'
    AUTH_URL = f'{BASE_URL}/oauth2/token'
    SEARCH_URL = f'{BASE_URL}/1.1/search/tweets.json'

    # OAUTH 2.0
    CLIENT = BackendApplicationClient(client_id=CLIENT_ID)
    OAUTH = OAuth2Session(client=CLIENT)

    def __init__(self):
        super().__init__()
        self._network = nx.Graph()

    @staticmethod
    def _authenticate():
        return TwitterScraper.OAUTH.fetch_token(token_url=TwitterScraper.AUTH_URL, client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET)

    def scrape(self):
        token = TwitterScraper._authenticate()
        nx.add_path(self._network, [0, 1], weight=7)
        return self._network
