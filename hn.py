from preferences import Preferences
import utils

from threading import Thread
from Queue import Queue
import datetime

# TODO: Find a way to 'cancel' all working threads when the user changes his input
# TODO: FIX error when typing "hn 4" (only 4 stories show up)
# TODO: I think the threading is messing up the order of the stories..

class HN:

    _preferences = None

    def set_preferences(self, preferences):

        # Initilize preferences
        self._preferences = preferences

    def load_top_stories(self, start_page):
        """ 
        Gets the desired number of top stories, 
        ignoring the first few equal to the value 
        of 'offset' passed in.
        """
        items_per_page = self._preferences.ITEM_AMOUNT
        pages_to_cache = self._preferences.CACHE_INCREMENT

        # Number of stories to load to get desired stories
        start_index = (items_per_page * start_page) - items_per_page
        stop_index = start_index + (pages_to_cache * items_per_page)

        # Get the ids
        ids_api_endpoint = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        ids = request_api(ids_api_endpoint)
        
        pages = []
        all_top_stories = []
        queue = Queue()
        for _x in range(5):
            story_api_endpoint = 'https://hacker-news.firebaseio.com/v0/item/'
            worker = HN_Worker(story_api_endpoint, queue, all_top_stories)
            worker.start()
        
        keep_order_flag = 0
        """
        for page_index in page_indexes:
            # Get stories
            start_id = page_index
            end_id = start_id + items_per_page
        """
        for index in range(start_index, stop_index):
            queue.put( (keep_order_flag, ids[index]) )
            keep_order_flag += 1

        queue.join()

        # Check if all the stories have been returned 

        all_top_stories.sort()
        all_top_stories = map(lambda x: x[1], all_top_stories)
        for page in utils.chunks(all_top_stories, items_per_page):
            pages.append(page)
        return pages

class HN_Worker(Thread):

    def __init__(self, download_link, queue, items):
        Thread.__init__(self)
        self._queue = queue
        self._url = download_link
        self._items = items
    
    def run(self):

        while True:
            order_key, story_id = self._queue.get()

            try:
                #Request API
                item_info = request_api('%s%s.json' % (self._url, story_id))
                
                # Check if the type is not a Story
                if item_info['type'] == 'story':
                    self._items.append( (order_key, Story(item_info)) )
                else:
                    pass # Display Invalid Story 
            finally:
                self._queue.task_done()

def request_api(url):
    import requests
    response = requests.get(url)
    return response.json()

class Story:
    def __init__(self, info):
        self.item_id = info['id']
        self.title = info['title']
        self.by = info['by']
        try:
            self.descendants = info['descendants']
        except:
            self.descendants = str(-1)
        self.url = info['url']
        self.time = info['time']
        self.score = info['score']
