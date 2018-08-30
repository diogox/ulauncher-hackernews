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
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

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

    def show_open_confirmation(self, number_of_links):
        confirmation = self._screens.render_open_confirmation(number_of_links)
        return RenderResultListAction(confirmation)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        argument = event.get_argument()

        # TODO: Check for invalid inputs like 'hn 1 2'
        # If the argument is not a digit, it's invalid
        # Otherwise, if it's non-existent, it defaults to 1
        # Any other digit is treated as a page number
        if argument is None:
            # If there are no arguments, default for a hard-coded 'top' subcommand
            # TODO: Add a preference to choose the default subcommand
            # Right now, the 'open' subcommand is defaulting to 'top' stories aswell. (Maybe have 'new' in the future)
            argument = 'top'

        arguments = argument.split()

        if arguments[0] == 'top':
            if len(arguments) >= 2:
                if arguments[1].isdigit():
                    page_number = arguments[1]
                else:
                    # TODO: Show error message
                    logger.info("********ERROR************ - %s" % argument)
                    return
            else:
                # Assume first page
                page_number = 1
            
            # TODO: Display error when there is no connection
            return extension.show_top_stories( int(page_number) )
        elif arguments[0] == 'open':
            if len(arguments) != 2:
                # TODO: Show error message
                logger.info("ERROR. Open number doesn't exist!")
                return
            
            number_of_links = arguments[1]
            if not number_of_links.isdigit():
                # TODO: Show error message
                logger.info("ERROR. Open number not digit!")
                return
            else:
                number_of_links = int(number_of_links)

            # Open the first links of top stories, equal to the number inputed
            return extension.show_open_confirmation(number_of_links)

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
        extension._preferences.update(event.id, event.new_value)
        logger.info("PREFERENCES: %s" % extension._preferences.CACHE_REFRESH_RATE)
        # Distribute preferences 
        extension._hn.set_preferences(extension._preferences) 
        extension._screens.set_preferences(extension._preferences)
        extension._cache.set_refresh_rate(extension._preferences.CACHE_REFRESH_RATE)
        extension._cache.set_items_per_page(extension._preferences.ITEM_AMOUNT)

class ItemEnterEventListener(EventListener):
    
    def on_event(self, event, extension):
        # This is activated upon clicking an item with a custom action
        # currently only used for opening a certain number of top stories
        import math
        import webbrowser
        number_of_links = event.get_data()

        n_of_pages = int(math.ceil(int(number_of_links) / float(extension._preferences.ITEM_AMOUNT)))
        # Load needed pages
        pages = extension._hn.load_top_stories(n_of_pages)
        logger.info('Numer of PAGES: %d' % n_of_pages)
        
        # Open the amount needed
        counter = 0
        for page in pages:
            for story in page:
                if counter < number_of_links:
                    webbrowser.open(story.url, new=1)
                    counter += 1

if __name__ == '__main__':
    HackernewsExtension().run()