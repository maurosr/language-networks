import json
import sys
import re

from collections import Counter
import itertools

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

import networkx as nx

class ClarinWordsGraphGenerator(object):
    
    def __init__(self):
        self._tokenizer = RegexpTokenizer(r'\w+')
        self._stop_words = set([x.upper() for x in stopwords.words('spanish')] + 
            ['DIJO', 'HABLÓ', 'PIDIÓ', 'TRAS', 'CÓMO', 'SI', 'VEZ', 'VA', 'SIGUE', 'BUSCA', 'PUEDE', 'AHORA',
                'INICIO', 'ARRANCA', 'ASÍ', 'DESPUÉS', 'CONTÓ', 'SALIÓ', 'SER', 'CREE', 'HACE', 'REVELÓ', 'ATRÁS',
                'FRASE', 'LUEGO', 'IR', 'RATIFICÓ', 'DIO', 'HABER', 'AÑOS',            
        ])

    def parse(self, dir, name, filename):
        news = []
        with open(filename) as f:
            for line in f:
                news.append(json.loads(line))
        
        titles = set()

        network = nx.Graph()
        
        word_counter = Counter()
        c = Counter()
        for news_json in news:
            for sentence in nltk.sent_tokenize(news_json['title'], language='spanish'):
                words = set(self._tokenize(sentence))
                for word in words:
                    #clean_title = ' '.join(self._tokenize(news_json['title']))
                    #titles.add(clean_title)
                    word_counter[word] += 1
                for w1, w2 in itertools.combinations(words, 2):
                    c[(min(w1, w2), max(w1, w2))] += 1
        
        for (w1, w2), weight in c.items():
            if word_counter[w1] >= 5 and word_counter[w2] >= 5 and weight > 1:
                nx.add_path(network, (w1, w2), weight=weight)
        
        self._write_csv(dir, name, titles, network)
        
    def _write_csv(self, dir, name, titles, network):
        with open('{}/{}_nodes.csv'.format(dir, name), 'w') as f:
            f.write('Id,Label,class\n')
            for i, node in enumerate(network.nodes):
                f.write('{},{},{}\n'.format(node, node, 0))

        with open('{}/{}_edges.csv'.format(dir, name), 'w') as f:
            f.write('Source,Target,Type,id,weight\n')
            for i, (src, trg, data) in enumerate(network.edges.data()):
                f.write('{},{},Undirected,{},{}\n'.format(src, trg, i, data["weight"]))
    
    def _tokenize(self, text):
        with_no_urls = re.sub(r"http\S+", "", text)
        words = self._tokenizer.tokenize(with_no_urls)
        return [w.upper() for w in words if w.upper() not in self._stop_words]  # + urls

            

def main():
    name = sys.argv[1]
    filename = sys.argv[2]
    dir = sys.argv[3]
    ClarinWordsGraphGenerator().parse(dir, name, filename)

if __name__ == '__main__':
    main()

