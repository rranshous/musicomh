# we want to pull the 2009 list + items. than move on the the archive.

from music_gigs_2009 import grab_listing as get_2009_listing
from music_gigs_2009_item import pull_item as get_2009_item
from music_gigs_archive import get_archive_list as get_archive_listing
from music_gigs_2009_item import pull_item as get_archive_item

from multiprocessing import Pool, Process, Pipe, Queue as PQueue
from Queue import Queue, Empty, Full
from threading import Thread

from urlparse import urljoin

import time
import sys
import os

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
                    try:
                        data = item_work_queue.get_nowait()
                        data.update(get_archive_item(data.get('item_link_href')))
                        item_result_queue.put_nowait(data)
                    except Exception, ex:
                        print 'item:',data
                        print 'item exception:',str(ex)
            except Exception, ex:
               #print 'EXCEPTION:',str(ex)
                raise


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
        print 'items:',item_work_queue.qsize(),
        print 'items/s:',(item_result_queue.qsize() / (time.time()-start)),
        print 'elapsed:',(time.time() - start)
        time.sleep(10)

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
            print 'item_url:',item.get('item_link_href')
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

def get_archive_both(threads=10,procs=None):
    # we are going to return a filled out item list

    start = time.time()

    # we are going to spawn a proc for each processor
    cores = os.sysconf("SC_NPROCESSORS_ONLN")

    # we are going to spawn up a process per core, and pool_size threads per proc

    # our functions
    def thread_run(index_work_queue,item_work_queue,item_result_queue):
        while not index_work_queue.empty() or not item_work_queue.empty() or item_result_queue.empty():
            try:
                # try and do some index processing
                if not index_work_queue.empty():
                    map(item_work_queue.put_nowait,get_archive_listing(index_work_queue.get_nowait()))
                if not item_work_queue.empty():
                    try:
                        data = item_work_queue.get_nowait()
                        r = get_archive_item(data.get('item_link_href'))
                        data.update(r)
                        item_result_queue.put_nowait(data)
                    except Empty:
                        continue
                    except Exception, ex:
                        print 'item:',data.get('item_link_href')
                        print 'item exception:',str(ex)
                        item_result_queue.put_nowait(data)
            except Empty:
                continue

            except Exception, ex:
               #print 'EXCEPTION:',str(ex)
                raise
        sys.exit(1)

    def proc_run(index_work_queue,item_work_queue,item_result_queue,pool_size):
        # we need to spawn up our threads
        threads = []
        for i in xrange(pool_size):
            thread = Thread(target=thread_run,
                            args=(index_work_queue,item_work_queue,item_result_queue))
            thread.start()
            threads.append(thread)
        # join + wait
        while [t for t in threads if t.is_alive()]:
            time.sleep(5)
        print 'THREADS DONE'
        for t in threads:
            t.join()
        print 'DONE JOINING'
        sys.exit(1)

    # our q's
    index_work_queue = PQueue(0)
    item_work_queue = PQueue(0)
    item_result_queue = PQueue(0)
    map(index_work_queue.put_nowait,get_archive_page_urls())

    # start our proc pool
    pool = []
    for i in xrange(procs or cores):
        proc = Process(target=proc_run,args=(index_work_queue,item_work_queue,item_result_queue,threads))
        proc.start()
        pool.append(proc)

    start_work = time.time()

    while not index_work_queue.empty() or not item_work_queue.empty() or item_result_queue.empty():
        print 'index:',index_work_queue.qsize(),
        print 'items:',item_work_queue.qsize(),
        print 'items/s:',(item_result_queue.qsize() / ((time.time()-start_work) or 1)),
        print 'elapsed:',(time.time() - start),
        print 'itemrs:',item_result_queue.qsize()
        time.sleep(10)

    #print 'JOINING PROCS'
    #for p in pool:
    #    p.join()
    for p in pool:
        if p.exitcode is not None: # might already be done
            p.join()
            print 'JOINED PROC'

    # pull our item list
    items = []
    while not item_result_queue.empty():
        items.append(item_result_queue.get(True,10))
    print 'TIME ELAPSED:',(time.time()-start)

    # and return
    return items


