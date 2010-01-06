# we are going to pull the archive pages and pull items for each of them

from urllib2 import urlopen
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup as BS
import re
from copy import copy
from music_gigs_2009 import _get_content as _base_get_content, massage_html, strip_tags

def get_archive_list(url):
    # grab our html
    lines = urlopen(url)
    html = ''.join(lines)
    soup = BS(massage_html(html))

    # classes:
    #  greybold = month / year (once per group)
    #  blackbasic = link
    classes = ['greybold','blackbasic']
    base_item = {'item_link_date':None}
    items = []
    for el in soup.findAll('td', {'class':lambda a: a in classes}):
        print 'el:',el
        if el.get('class') == 'greybold':
            # it's the date
            base_item['item_link_date'] = _base_get_content(el)
        else:
            item = copy(base_item)
            item['item_link_text'] = _base_get_content(el)
            items.append(item)

    return items
