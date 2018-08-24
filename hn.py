from hackernews import HackerNews
from preferences import Preferences

import datetime

class HN:

    _preferences = None
    _api = None

    def __init__(self):

        # Initialize HackerNews API
        self._api = HackerNews()

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
        ids = self._api.top_stories(limit=int(total_number))

        # Get stories
        end_id = total_number
        start_id = end_id - items_per_page
        
        top = []
        for index in range(start_id, end_id):
            story = self._api.get_item( ids[index] )
            top.append(story)

        return top

def get_page_number(starts_at, number_of_items_per_page):
    return (int(starts_at)/int(number_of_items_per_page)) + 1