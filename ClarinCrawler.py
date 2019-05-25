import requests
import json
import sys
from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
import re

def _get_links(pages, limit):
    url = 'https://www.clarin.com/dinreq/sas/paginator/2/NWS/latest/2-result.json?tpl=desgenericolistadoautomaticov3mo_subhome_3col_iscroll.tpl&pages={}&start=0&share_view=0&limit={}'.format(pages, limit)
    response = requests.get(url)
    relative_links = list(dict.fromkeys(re.findall('\/politica([^\"]*)', response.text)))
    return ['https://www.clarin.com{}'.format(rl.replace('\\', '')) for rl in relative_links]


def _get_text_object(url, category):
    return _parse_news(requests.get(url), category)


def _parse_news(response, category):
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('div', {'class':'body-nota'})
    text_parragraphs = [p.get_text() for p in body.find_all("p")]
    if 'Recibir newsletter' in text_parragraphs:
    	text_parragraphs.remove('Recibir newsletter')
    news_text = '\n'.join(text_parragraphs).strip()
    
    title = soup.find('div', {'class':'title'})
    
    title_text = title.find('h1', {'id':'title'}).get_text()
    
    return {"content": news_text, "title" : title_text, "url": response.url, 'category': category}

def main():
    pages = int(sys.argv[1])
    limit = int(sys.argv[2])
    processes = int(sys.argv[3])
    
    links = _get_links(pages, limit)

    tp = ThreadPool(processes = processes)
    responses = tp.imap(requests.get, links)
    
    for response in responses:
        print(json.dumps(_parse_news(response, 'politics')))

if __name__ == '__main__':
    main()

