# we are going to pull the archive pages and pull items for each of them

from urllib2 import urlopen
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup as BS
import re
from copy import copy
from music_gigs_2009 import _get_content as _base_get_content, massage_html, strip_tags

def _get_feature(el,url):
    return { 'is_feature':1,
             'item_link_href': urljoin(url,el.contents[3].get('href')),
             'item_link_subheading': str(el.contents[4].strip()),
             'item_link_heading': strip_tags(str(el.contents[3]).strip()),
             'item_link_date': strip_tags(str(el.contents[4])).strip() }

def _get_in_pictures(el,url):
    return { 'is_in_pictures':1,
             'item_link_href': urljoin(url,el.contents[3].get('href')),
             'item_link_subheading': str(el.contents[4].strip()),
             'item_link_date': strip_tags(str(el.contents[4]).strip()),
             'item_link_heading': strip_tags(str(el.contents[3])).strip() }

def _get_normal(el,url):
    content = _base_get_content(el)
    if not content: return {}
    return { 'item_link_heading': content,
             'item_link_href': urljoin(url,el.contents[1].get('href')),
             'item_link_subheading': el.contents[2].strip(),
             'item_link_date': strip_tags(str(el.contents[3])).strip() }

def get_archive_list(url):
    # grab our html
    lines = urlopen(url)
    html = ''.join(lines)
    soup = BS(massage_html(html))

    # classes:
    #  greybold = month / year (once per group)
    #  blackbasic = link
    classes = ['greybold','blackbasic']
    base_item = {'item_link_group_date':None}
    items = []
    for el in soup.findAll('td', {'class':lambda a: a in classes}):
        if el.get('class') == 'greybold':
            # it's the date
            base_item['item_link_group_date'] = _base_get_content(el)
        else:
            # could be a pic line or could be a normal
            item = copy(base_item)
            all_content = ''.join([str(x).lower() for x in el.contents])
            # if picture
            if 'in pictures:' in all_content:
                item.update(_get_in_pictures(el,url))
            # if feature
            elif 'feature:' in all_content:
                item.update(_get_feature(el,url))
            # if normal
            else:
                item.update(_get_normal(el,url))
                if not item.get('item_link_heading'): continue
            items.append(item)

    return items
