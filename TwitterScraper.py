import networkx as nx

from Scrapper import Scraper


class TwitterScraper(Scraper):
    def __init__(self):
        super().__init__()
        self._network = nx.Graph()

    def scrape(self):
        nx.add_path(self._network, [0, 1], weight=7)
        return self._network
