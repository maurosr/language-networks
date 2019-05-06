from TwitterScraper import TwitterScraper


class NetworkBuilder(object):

    def __init__(self, scraper):
        self._scraper = scraper
        self._network = None

    def build(self):
        self._network = self._scraper.scrape()

    def write_csv(self, filename):
        with open(filename, 'w') as f:
            f.write('Source,Target,Type,id,weight\n')
            for i, (src, trg, data) in enumerate(self._network.edges.data()):
                f.write(f'{src},{trg},Undirected,{i},{data["weight"]}\n')


if __name__ == '__main__':
    output_filename = 'data/language_network.csv'
    twitter_scraper = TwitterScraper()
    builder = NetworkBuilder(twitter_scraper)

    builder.build()
    builder.write_csv(output_filename)
