from datetime import datetime
import utils

class Cache:
    
    def __init__(self):
        self.clear_cache()

    def set_refresh_rate(self, cache_refresh_rate):
        self._refresh_rate = cache_refresh_rate

        # If it's no longer valid, clear
        if not self.is_cache_valid():
            self.clear_cache()

    def set_items_per_page(self, items_per_page):
        self._items_per_page = items_per_page

        # Cache no longer viable, delete it
        self.clear_cache()

    def add_page(self, page_number, items):
        """
            Adds Items to be cached
        """
        self._cached_items[page_number] = items
        self._cached_at = utils.get_current_time()

    def get_page(self, page_number):
        """
            Returns items from the desired page
            (according to the number of items per page specified).
            If the page doesn't exist, returns None.
        """
        # Check if the cache has expired
        if not self.is_cache_valid():
            self.clear_cache()
            return None
            
        # Check if the desired page exists
        if page_number in self._cached_items:
            return self._cached_items[page_number]
        else:
            # Return nothing, the page doesn't exist
            return None
    
    def is_cache_valid(self):
        """
            Checks if the cache has expired.
        """

        # Check if there is anything cached
        if isinstance(self._cached_at, datetime):
            # Check if it has expired
            now = utils.get_current_time()
            minutes_passed = utils.get_time_difference_in_minutes(self._cached_at, now)
            return minutes_passed < self._refresh_rate          
        else:
            # No cache available
            return False

    def clear_cache(self):
        self._cached_items = {}
        self._cached_at = ""