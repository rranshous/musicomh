# we want to pull the 2009 list + items. than move on the the archive.

from music_gigs_2009 import grab_listing as get_2009_listing
from music_gigs_2009_item import pull_item as get_2009_item

from multiprocessing import Pool, Process, Pipe

import time

LISTING_BASE_URL_2009 = 'http://musicomh.com/music/gigs/'

def wrap_pipe(*args,**kwargs):
    pipe = kwargs.get('pipe')


def get_2009(pool_size=4):
    # first pull down our item data from the listing
    items = get_2009_listing(LISTING_BASE_URL_2009)
    # now we want to extend our item data by pulling the item details
    # one by one from the individual pages
    start = time.time()
    pool = Pool(pool_size)
    for i,item_data in enumerate(items):
        # pull it's page
        #item_data.update(get_2009_item(item_data.get('item_link_href')))

        # try async this shit
        pool.apply_async(get_2009_item,(item_data.get('item_link_href'),),
                         callback=item_data.update)

    pool.close()
    pool.join()
    print 'time elapsed:',(time.time() - start)

    # we should now have all the info for 2009
    return items

