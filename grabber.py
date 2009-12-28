# we want to try and grab a dir of the site + create a data set for each
# review (or w/e)

from diskdb.Blip import Blip
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup as BS
import re

# get the content from an item
def _get_content(items):
    if not isinstance(items,list):
        items = [items]
    to_return = []
    for item in items:
        print 'C:',item.contents
        content = [str(c).strip() for c in item.contents if str(c).strip()]
        content = content[0]
        # strip the html
        content = re.sub(r'<[^>]*?>','',content)
        to_return.append(content)
    return to_return

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
    for item_data in zip(*tuple([
                            soup.findAll('td',{'class':c)]) for c,n in classes)):
        item = {}
        for i,(c,n) in enumerate(classes):
            print 'D:',item_data[i]
            item[n] = _get_content(item_data[i])
            # we are also on the lookout for the url
            #if item_data[i][0]
        items.append(item)
    return items

    items = [dict(zip([n for c,n in classes],x)) for x in
                zip(*tuple([_get_content(soup.findAll('td',{'class':c}))
                    for c,n in classes]))]

    return items










