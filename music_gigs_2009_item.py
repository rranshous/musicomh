# pull the item data

from BeautifulSoup import BeautifulSoup as BS
from urllib2 import urlopen,HTTPError
from music_gigs_2009 import _get_content as _base_get_content, massage_html, strip_tags
import re

def _get_content_(elements):
    # use the base
    return ' '.join(map(_base_get_content,elements))

def _get_content_item_heading(elements):
    return unicode(elements[0].contents[2]).strip() or unicode(elements[0].contents[4]).strip()

def _get_content_item_content(elements):
    # the content is spread out through many elements
    # different elements = line breaks
    # br = line breaks
    to_return = []
    for el in elements:
        for content in el.contents:
            # we want the string, not the bs from soup
            content = unicode(content)
            # we don't want blank lines, or bullshit, bullshit = all caps?
            if content.upper() == content: continue
            if content.strip() == '': continue # don't need blank lines
            # don't need non-content bs, which means if we start w/
            # a bad tag, rejected
            good_tags = ['p','b']
            if content[0] == '<' and content[1] not in good_tags: continue
            if ''.join(content.strip().split()).lower() == '<br/>':
                # this is a line break
                to_return.append('')
            else:
                to_return.append(strip_tags(content).strip())
    return "\n".join(to_return)

def _get_content_item_author(elements):
    if not elements: return ''
    return strip_tags(str(elements[0].contents[1])).strip()

def pull_item(url):
    # we are going to pull down the html for the item page
    # try and grab the relevant data + return back a dict

    if not url:
        return {}

    # grab the html
    try:
        lines = urlopen(url)
    except HTTPError, ex:
        print 'EXCEPTION:',url,str(ex)
        return {}

    html = massage_html(''.join(lines))
    try:
        soup = BS(html)
    except Exception, ex:
        print 'EXCEPTION:',url,len(html)
        #raise
        return {}

    # classes:
    #  blackbig = heading
    #  blackit = subheading # only the first is the subheading
    #  blackbasic = content
    #  blackitalic = author
    classes = [('td','blackbig','item_heading'),
               ('td','blackit','item_subheading'),
               ('td','blackbasic','item_content'),
               ('div','blackitalic','item_author')]

    # we are going to pull the item's info
    item = {'item_url':url}
    function_base = '_get_content_'
    for t,c,n in classes:
        elements = soup.findAll(t,{'class':c})
        fn = globals().get(function_base+n) or globals().get(function_base)
        content = fn(elements)
        item[n] = content

    # there might be articles with multiple pages
    page = 1
    if 'Page %s' in html:
        # follow to the next page and grab the content
        pass

    # if the item doesn't have an author, than the tag is probably malformed
    if not item.get('item_author'):
        item['item_author'] = strip_tags(re.findall(r'(>-.*</)',html)[0])[3:-2].strip()

    return item
