# we want to pull the 2009 list + items. than move on the the archive.

from music_gigs_2009 import grab_listing as get_2009_listing
from music_gigs_2009_item import pull_item as get_2009_item
from music_gigs_archive import get_archive_list as get_archive_listing
from music_gigs_2009_item import pull_item as get_archive_item

from multiprocessing import Pool, Process, Pipe
from Queue import Queue
from threading import Thread

from urlparse import urljoin

import time

LISTING_BASE_URL_2009 = 'http://musicomh.com/music/gigs/'


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

def get_archive_page_urls():
    # for now we are just returning back the ~hardcoded list
    return [urljoin('http://musicomh.com/music/gigs/','index-%s.htm' % i)
                for i in xrange(2008,1999,-1)]

def get_archive_threads(pool_size=4):
    # we are going to try and do the same as get_archive
    # but using threads instead of processes
    start = time.time()
    items = []

    def do_the_work(index_work_queue,item_work_queue,item_result_queue):
        while not index_work_queue.empty() or not item_work_queue.empty():
            try:
                # try and do some index processing
                if not index_work_queue.empty():
                    map(item_work_queue.put_nowait,get_archive_listing(index_work_queue.get_nowait()))
                elif not item_work_queue.empty():
                    data = item_work_queue.get_nowait()
                    data.update(get_archive_item(data.get('item_link_href')))
                    item_result_queue.put_nowait(data)
            except Exception, ex:
                print 'EXCEPTION:',str(ex)
            
            
    # load up the queues
    index_work_queue = Queue(0)
    item_work_queue = Queue(0)
    item_result_queue = Queue(0)
    map(index_work_queue.put_nowait,get_archive_page_urls())

    # setup the threads
    threads = []
    for i in xrange(pool_size):
        thread = Thread(target=do_the_work,
                        args=(index_work_queue,item_work_queue,item_result_queue))
        thread.start()
        threads.append(thread)

    # wait for our queues to empty
    while not item_work_queue.empty() or not index_work_queue.empty() or item_result_queue.empty():
        print 'index:',index_work_queue.qsize(),
        print 'items:',item_work_queue.qsize()
        time.sleep(1)

    # make sure they are done
    for thread in threads:
        thread.join()
        
    print 'TIME ELAPSED:',(time.time() - start)

    # and get our results
    items = [i for i in item_result_queue.get_nowait()]

    return items

def get_archive(pool_size=4):
    # we are going to pull the archive list pages for 2008-2000
    # and than pull the pages to fill in the item data

    start = time.time()
    items = []
    pool = Pool(pool_size)

    # this method is going to be the callback for getting the item list back
    # from the archive list pages
    def handle_items(page_items):
        # we are going to add our item to the item list and than updat it's info
        for item in page_items:
            items.append(item)
            pool.apply_async(get_archive_item,(item.get('item_link_href'),),
                         callback=item.update)

    # pull all the archive items
    list_results = []
    for page_url in get_archive_page_urls():
        r = pool.apply_async(get_archive_listing,(page_url,),callback=handle_items)
        list_results.append(r)

    # wait for the lists to be processed
    while [x for x in list_results if not x.ready()]:
        time.sleep(1)

    pool.close()
    pool.join()

    print 'time elapsed:',(time.time() - start)

    return items











