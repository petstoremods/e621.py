#!/usr/bin/env python3

import re
import urllib.request
import time
import os, sys

PORN_DUMP_SIZE = 39
POST_LIMIT = PORN_DUMP_SIZE

CACHE_FILE_NAME = '.previous_e621_matches'
PREVIOUS_MATCHES = set(open(CACHE_FILE_NAME).read().split())

TEMP_FOLDER = 'tmp'

REQUEST_SLEEP_TIME_SECONDS = 0.5 # be nice to the site 
BASE_URL = 'https://e621.net/'
BASE_SEARCH_URL = f'{BASE_URL}posts?tags='
TAGS = [
    'order:random',
    'score:>666',
    'rating:e'
]

BAN_TAGS = [
    'comic',
    'animation',
    'young',
    'scat'
]
BAN_TAGS = list(map(lambda tag: '-' + tag, BAN_TAGS))

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
HEADERS = {'User-Agent': USER_AGENT,}

def join_tags(tags):
    result = ''
    for tag in tags:
        result += tag.replace(':', '%3A')
        result += '+'

    return result[:-1]

def get_html(url):
    print(f'Requesting: {url}...')
    time.sleep(REQUEST_SLEEP_TIME_SECONDS)
    request = urllib.request.Request(url, None, HEADERS)
    response = urllib.request.urlopen(request)
    return response.read()

OPENER_SET = False
def download_url(url):
    global OPENER_SET
    
    print(f'Requesting: {url}...')
    time.sleep(REQUEST_SLEEP_TIME_SECONDS)

    if not OPENER_SET:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        OPENER_SET = True
        
    name = str(int(time.time() * 100))
    ext = os.path.splitext(url)[1]
    urllib.request.urlretrieve(url, f'{TEMP_FOLDER}/{name}{ext}')

def get_search_results_page(tags, exclude):
    url = BASE_SEARCH_URL + join_tags(tags) + '+' + join_tags(exclude)
    return get_html(url)

def get_matching_images(tags=TAGS, excludes=BAN_TAGS):
    search_page = get_search_results_page(tags, excludes)
    posts = re.findall(b"posts\/\d+", search_page)

    print('Obtaining matches...')
    links = []
    for post in posts:
        post_string = post.decode('ascii')
        link = f'{BASE_URL}{post_string}'
        links.append(link)

    if POST_LIMIT != 0 and len(links) > POST_LIMIT:
        links = links[:POST_LIMIT]
        
    print('Getting download links...')
    download_links = []
    for link in links:
        link_page = get_html(link)
        download_link_match = re.search(b"data-file-url=\"[^\s]+", link_page)
        download_link = link_page[download_link_match.start() : download_link_match.end()]

        download_link = download_link.decode('ascii')
        
        download_link = download_link[download_link.find('https:'):-1]
        download_links.append(download_link)
        
    return download_links

def update_cache(links):
    text = ''
    for link in PREVIOUS_MATCHES:
        text += link + '\n'

    for link in links:
        text += link + '\n'

    open(CACHE_FILE_NAME, 'w').write(text)

def download_images(image_links):
    print('Downloading images...')
    for link in image_links:
        download_url(link)
    
def generate_porn_dump(theme):
    tags = TAGS
    if theme:
        tags.append(theme)
        
    image_links = set()
    while len(image_links) < PORN_DUMP_SIZE:
        image_links.update(get_matching_images(tags))
        image_links -= PREVIOUS_MATCHES

    download_images(image_links)
    update_cache(image_links)

def set_dump_size(dump_size, limit=0):
    global PORN_DUMP_SIZE
    global POST_LIMIT

    PORN_DUMP_SIZE = dump_size
    POST_LIMIT = limit
    
def main():
    global PORN_DUMP_SIZE
    theme = None
    if len(sys.argv) > 1:
        set_dump_size(10, 10)
        theme = sys.argv[1]
    
    generate_porn_dump(theme)
    print('Done!')

if __name__ == '__main__':
    main()

