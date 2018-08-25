import json
import logging
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)

import datetime

from hn import HN
from preferences import Preferences
from screens import Screens
from cache import Cache

# TODO: Certain items of an extended length can be impossible to read because they get truncated
class HackernewsExtension(Extension):

    _preferences = Preferences()
    _screens = Screens()
    _hn = HN()
    _cache = Cache()

    def __init__(self):
        super(HackernewsExtension, self).__init__()

        # Subscribe to events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener()) # Set preferences to inner members
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def show_top_stories(self, load_page_number):

        # Check if the page is cached
        cached_page = self._cache.get_page(load_page_number)

        if cached_page:
            return RenderResultListAction(cached_page)
        else:
            stories = self._hn.load_top_stories(load_page_number)
            items = self._screens.render_top_stories(stories[0], load_page_number)
            
            # Cache first item
            self._cache.add_page(load_page_number, items)

            # Cache items
            for i in range( 1, len(stories) ):
                page_number = load_page_number + i
                current_items = self._screens.render_top_stories(stories[i], page_number)
                self._cache.add_page(page_number, current_items)

        return RenderResultListAction(items)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        page_number = event.get_argument()

        # TODO: Check for invalid inputs like 'hn 1 2'
        # If the argument is not a digit, it's invalid
        # Otherwise, if it's non-existent, it defaults to 1
        # Any other digit is treated as apage number
        if not page_number:
            # If no page is specified, assume first page
            page_number = 1
        elif not page_number.isdigit():
            # Show, and return, error message
            pass

        # TODO: Display error when there is no connection
        return extension.show_top_stories( int(page_number) )

class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):

        # Set Preferences (and check fr errors)
        extension._preferences.set_preferences(event.preferences)

        # Distribute preferences 
        extension._hn.set_preferences(extension._preferences) 
        extension._screens.set_preferences(extension._preferences)
        extension._cache.set_refresh_rate(extension._preferences.CACHE_REFRESH_RATE)
        extension._cache.set_items_per_page(extension._preferences.ITEM_AMOUNT)

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        extension._preferences.update()

        # Distribute preferences 
        extension._hn.set_preferences(extension._preferences) 
        extension._screens.set_preferences(extension._preferences)
        extension._cache.set_refresh_rate(extension._preferences.CACHE_REFRESH_RATE)
        extension._cache.set_items_per_page(extension._preferences.ITEM_AMOUNT)

if __name__ == '__main__':
    HackernewsExtension().run()