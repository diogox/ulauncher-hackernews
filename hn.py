from hackernews import HackerNews
from preferences import Preferences

from threading import Thread
from Queue import Queue
import datetime

class HN:

    _preferences = None

    def set_preferences(self, preferences):

        # Initilize preferences
        self._preferences = preferences

    def load_top_stories(self, page_number):
        """ 
        Gets the desired number of top stories, 
        ignoring the first few equal to the value 
        of 'offset' passed in.
        """
        items_per_page = self._preferences.ITEM_AMOUNT

        # Number of stories to load to get desired stories
        total_number = items_per_page * page_number

        # Get the ids
        ids_api_endpoint = 'https://hacker-news.firebaseio.com/v0/topstories.json'
        ids = request_api(ids_api_endpoint)

        # Get stories
        end_id = total_number
        start_id = end_id - items_per_page
        
        top = []
        queue = Queue()
        for _x in range(5):
            story_api_endpoit = 'https://hacker-news.firebaseio.com/v0/item/'
            worker = HN_Worker(story_api_endpoit, queue, top)
            worker.start()
        
        for index in range(start_id, end_id):
            queue.put(ids[index])

        queue.join()
        return top

class HN_Worker(Thread):

    def __init__(self, download_link, queue, items):
        Thread.__init__(self)
        self._queue = queue
        self._url = download_link
        self._items = items
    
    def run(self):

        while True:
            story_id = self._queue.get()

            try:
                #Request API
                item_info = request_api('%s%s.json' % (self._url, story_id))
                self._items.append( Story(item_info) )
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
        self.descendants = info['descendants']
        self.url = info['url']
        self.time = info['time']
        self.score = info['score']
