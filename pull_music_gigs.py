# we want to pull the 2009 list + items. than move on the the archive.

from music_gigs_2009 import grab_listing as get_2009_listing
from music_gigs_2009_items import pull_items as get_2009_item

LISTING_BASE_URL_2009 = 'http://musicomh.com/music/gigs/'

def get_2009():
    # first pull down our item data from the listing
    items = grab_listing(LISTING_BASE_URL_2009)
    # now we want to extend our item data by pulling the item details
    # one by one from the individual pages
    for item_data in items.items():
        
