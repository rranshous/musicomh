# we want to try and grab the gigs
# dir of the site + create a data set for each
# review (or w/e)

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup as BS
import re
from urlparse import urlparse

# get the content from an item
def _get_content(item):
    content = [str(c).strip() for c in item.contents if str(c).strip()]
    content = content[0]
    # strip the html
    content = re.sub(r'<[^>]*?>','',content)
    return content

def get_content(items):
    return map(items,_get_content)

def grab_listing(url):
    # we are going to grab the listing page and return back
    # dicts of data for each listed item

    # grab the page
    lines = urlopen(url)

    # go through the output
    html = ''.join(lines)
    # due to gay script tag
    html = html.replace("</scri'+'pt>",'</script>')
    soup = BS(html)

    # classes:
    #  black20 = heading of item
    #  blackitalic = headline details
    #  blackbasic = item summary
    classes = [('black20','item_link_heading'),
               ('blackitalic','item_link_subheading'),
               ('blackbasic','item_link_description')]

    # we are going to go through the soup looking for items in the classes
    # listed above, they should be in sets
    # we are grabbing the first line of the element content as the item value
    # [ {classes[1]:value(classes[0])}, {.. ]

    items = []
    soup_items = zip(*[soup.findAll('td',{'class':c}) for c,n in classes])
    for item_data in soup_items:
        item = {}
        for i,d in enumerate(item_data):
            item[classes[i][1]] = _get_content(d)
            # we also want to grab the url for the item's page
            if d.contents[1].get('href'):
                item['item_link_href'] = urljoin(url,d.contents[1].get('href'))
        items.append(item)
    return items


