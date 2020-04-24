
import re
import time
from urllib import request
from urllib.parse import urljoin
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from process_data import clean_text

def to_keep(para, len_thres = 10):
    """
    Applies exclusion criteria on a block of text by regex patterns and 
    word count length. 

    Args:
        para (str): text input
        len_thres (int): minimum word count length for text to be kept. 
            Defaults to 10
    
    Returns:
        bool: True if passed filtering criteria, False otherwise
    """

    if para == '' or len(para.split()) < len_thres:
        return False
    
    pattern = '^RELATED: '
    pattern += '|follow (her|him|them) on (Instagram|Twitter|Snapchat|Tumblr)'
    pattern += '|Refinery29|PureWow'
    pattern += '|[sS]hop [tT]his|[bB]uy [tT]his'

    if re.search(pattern, para):
        return False
        
    return True


def get_article_links(base_url, tags, links_to_excl = ' ', links_to_incl = ''):
    """
    Collects relevant hyperlinks from a given webpage.

    Args:
        base_url (str): webpage to look for links
        tags (list of tuples): attributes by which to look for relevant links. 
            For example, `(div, id, post-123)` means looking for `div` with the 
            id post-123.
        links_to_excl (str): regular expression pattern of hyperlinks to exclude.
            Defaults to no criteria (i.e. keep all links)
        links_to_incl (str): regular expression pattern of hyperlinks to keep.
            Defaults to no criteria (i.e. keep all links)
    
    Returns:
        list of str: list of links
    """

    r = request.urlopen(base_url).read()
    soup = BeautifulSoup(r)

    articles = soup.find_all(
        lambda tag: any([tag.name == x1 and tag.get(x2) == x3 
                         for x1, x2, x3 in tags])
    )

    urls = []

    for article in articles:

        links = article.find_all('a', href = True)

        for link in links:
        
            url = urljoin(base_url, link['href'])

            if (url not in urls) and \
               (not re.search(links_to_excl, url)) and \
               (re.search(links_to_incl, url)):

               urls.append(url)

    return urls


def get_article_text(url, tags, in_chunks = False, split_on = '\n'):
    """
    Scrape text content from a webpage.

    Args:
        url (str): link to webpage to scrape
        tags (list of tuples): attributes by which to look for relevant text blocks. 
            For example, `(div, id, post-123)` means looking for `div` with the 
            id post-123.
        in_chunks (bool): whether to look for all occurrences of the tags, or 
            just the single instance. Defaults to False 
        split_on (str): if a single block of text, how to split into 
            chunks/paragraphs. Defaults to '\n'
    
    Returns:
        list of str: list of text chunks from given webpage
    """

    r = request.urlopen(url).read()
    soup = BeautifulSoup(r)

    if in_chunks:

        raw_text = soup.find_all(
            lambda tag: any([tag.name == x1 and tag.get(x2) == x3 
                             for x1, x2, x3 in tags])
        )

        raw_text_s = [para.getText(separator = ' ') for para in raw_text]

    else:

        raw_text = soup.find(
            lambda tag: any([tag.name == x1 and tag.get(x2) == x3 
                             for x1, x2, x3 in tags])
        ).getText(separator = ' ')

        raw_text_s = re.split(split_on, raw_text)
    
    return raw_text_s


def clean_article_text(text_chunks):
    """
    Cleans and filters text chunks (e.g. remove text that are too short).

    Args:
        text_chunks (list of str): list of raw text chunks to be processed
    
    Returns:
        list of str: list of cleaned up text chunks that passed filtering criteria
    """

    cleaned_text = list(filter(
        to_keep,
        [clean_text(t) for t in text_chunks]
    ))

    return cleaned_text


if __name__ == '__name__':

    # Specify sites to scrape and specifications for searching links/text
    article_configs = {}

    article_configs['purewow'] = {
        'base_urls': ['https://www.purewow.com/wellness/Horoscopes'],
        'tags_main': [
            ('div', 'class', ['col-sm-4']), 
            ('div', 'class', ['col-sm-3'])
        ],
        'links_to_excl': 'memes|quiz',
        'links_to_incl': '',
        'tags_post': [
            ('article', 'class', ['component__article--wide', 'post']),
            ('section', 'id', 'articleText'),
            ('div', 'class', ['post-description'])
        ],
        'in_chunks': False,
        'split_on': '\n'
    }

    article_configs['refinery29'] = {
        'base_urls': ['https://www.refinery29.com/en-ca/search?q=horoscope'],
        'tags_main': [('div', 'id', 'below-the-fold-modules')],
        'links_to_excl': ' ',
        'links_to_incl': '',
        'tags_post': [('div', 'class', ['section-outer-container'])],
        'in_chunks': True,
        'split_on': '\n'
    }
    
    article_configs['astrogrlz'] = {
        'base_urls': ["https://www.astrogrlz.com/blog"],
        'tags_main': [('main', 'class', ['Main', 'Main--blog-list'])],
        'links_to_excl': ' ',
        'links_to_incl': '/blog/(?!tag)',
        'tags_post': [('main', 'class', ['Main', 'Main--blog-item'])],
        'in_chunks': False,
        'split_on': '\n|\xa0'
    }

    article_configs['lovelanyadoo'] = {
        'base_urls': [
            "https://www.lovelanyadoo.com/weekly-horoscope",
            "https://www.lovelanyadoo.com/weekly-horoscope?offset=1580876610999",
            "https://www.lovelanyadoo.com/weekly-horoscope?offset=1574830800339"
        ],
        'tags_main': [('main', 'class', ['Main', 'Main--blog-list'])],
        'links_to_excl': ' ',
        'links_to_incl': 'horoscope/',
        'tags_post': [('main', 'class', ['Main', 'Main--blog-item'])],
        'in_chunks': False,
        'split_on': '\n|\xa0'
    }

    article_configs['demetra'] = {
        'base_urls': ["https://demetra-george.com/category/blog/"],
        'tags_main': [('div', 'class', ['nv-index-posts', 'blog', 'col'])],
        'links_to_excl': ' ',
        'links_to_incl': '/blog/(?!page)',
        'tags_post': [('div', 'class', ['nv-content-wrap', 'entry-content'])],
        'in_chunks': False,
        'split_on': '\n'
    }

    article_configs['astrologycom'] = {
        'base_urls': [
            "https://www.astrology.com/us/editorial/editorial-article-list-tag.aspx?ArticleTag_alphanames=Stellar+Guidance&page=1",
            "https://www.astrology.com/us/editorial/editorial-article-list-tag.aspx?ArticleTag_alphanames=Stellar+Guidance&page=2",
            "https://www.astrology.com/us/editorial/editorial-article-list-tag.aspx?ArticleTag_alphanames=Stellar+Guidance&page=3"
        ],
        'tags_main': [('section', 'class', ['grid', 'index-article'])],
        'links_to_excl': ' ',
        'links_to_incl': '/article/',
        'tags_post': [('section', 'class', ['article', 'grid', 'grid-right-sidebar', 'primis-rr'])],
        'in_chunks': False,
        'split_on': '\n'
    }


    # Scrape each site for astrology-related content and clean up texts
    for site in article_configs:

        links = []

        for url in article_configs[site]['base_urls']:

            links += get_article_links(
                url, 
                article_configs[site]['tags_main'],
                article_configs[site]['links_to_excl'],
                article_configs[site]['links_to_incl']
            )

        for link in links[:100]:
            
            try:

                raw_text_s = get_article_text(
                    link, 
                    article_configs[site]['tags_post'],
                    article_configs[site]['in_chunks'],
                    article_configs[site]['split_on']
                )
            
            except HTTPError as e:

                if e.code == 429:
                    
                    print('Too many requests...waiting to retry')
                    time.sleep(60 * 2)
                    raw_text_s = get_article_text(
                        link, 
                        article_configs[site]['tags_post'],
                        article_configs[site]['in_chunks'],
                        article_configs[site]['split_on']
                    )

                else:
                    raise Exception(f'HTTPError encountered when trying to scrape {link}')

            with open(f'data/raw/{site}.txt', 'a', encoding = 'utf-8') as f:
                f.write('\n'.join(raw_text_s) + '\n')
            
            cleaned_text = clean_article_text(raw_text_s)

            with open(f'data/cleaned/{site}_cleaned.txt', 'a') as f:
                f.write('\n'.join(cleaned_text) + '\n')


    # Combine all text into a single file
    lines = []
    for site in article_configs:
        with open(f'data/cleaned/{site}_cleaned.txt', 'r') as f:
            lines += [line.strip() for line in f.readlines()]

    with open('data/final/article_data.txt', 'w') as f:
        f.write('\n'.join(lines))

