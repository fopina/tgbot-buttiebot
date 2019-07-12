#!/usr/bin/env python

from __future__ import print_function
import requests
import re
import json


PICLOAD = 50
HASH = '42323d64886122307be10013ad2dcc44'

def url_and_caption(media):
    try:
        c = media['edge_media_to_caption']['edges'][0]['node']['text']
    except KeyError:
        c = ''
    media['caption'] = c
    return media

def strip_pics(data):
    return (
        [
            url_and_caption(x['node'])
            for x in data['edges']
        ],
        data['page_info']['has_next_page'],
        data['page_info']['end_cursor']
    )

def scrape(username):
    s = requests.Session()
    r = s.get('https://www.instagram.com/%s/?__a=1' % username)
    j = r.json()['graphql']['user']
    user_id = j['id']
    pics, keepgoing, cursor = strip_pics(j['edge_owner_to_timeline_media'])

    for pic in pics:
        yield pic

    while keepgoing:
        r = s.get(
            'https://www.instagram.com/graphql/query/',
            params={
                'query_hash': HASH,
                'variables': '{"id":"%s","first":%d,"after":"%s"}' % (user_id, PICLOAD, cursor)
            }
        )
        pics, keepgoing, cursor = strip_pics(json.loads(r.text)['data']['user']['edge_owner_to_timeline_media'])
        for pic in pics:
            yield pic

def main(args):
    for u in args:
        print('Scraping %s...' % u)
        for p in scrape(u):
            print(' - %s' % p)
        print()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
