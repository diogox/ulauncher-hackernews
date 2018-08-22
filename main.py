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

# TODO: Certain items of an extended length can be impossible to read because they get truncated
class HackernewsExtension(Extension):

    def __init__(self):
        super(HackernewsExtension, self).__init__()

        # Amount of stories to display
        self.SHOW_AMOUNT = 5

        # API limit of stories (A multiple of the SHOW_AMOUNT constant is best)
        self.LIMIT_STORIES = 15

        # Refresh rate (in minutes) for cached data
        self.REFRESH_RATE = 5

        # Initialize HackerNews API
        from hackernews import HackerNews
        self.hn_api = HackerNews()

        self.cached_data = {
            "stories": []
        }
        #self.load_and_cache_data()

        # Subscribe to events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        #self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def load_and_cache_data(self, until_story_index = -1):

        # Get story ids
        limit = self.LIMIT_STORIES
        if until_story_index >= 0:
            limit = until_story_index + self.LIMIT_STORIES

        stories_ids = self.hn_api.top_stories(limit=limit)

        # Check for connection issues
        if not stories_ids:
            raise NameError('ConnectionError')

        now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)
        
        # Get stories
        stories = []
        for story_id in stories_ids:
            story = self.hn_api.get_item(story_id)
            stories.append(story)

        # Cache data
        self.cached_data = {
            "stories": stories,
            "cached_at": now
        }

    def show_menu(self):
        keyword = self.preferences['keyword']

        MENU_ITEMS = [
            ExtensionResultItem(icon='images/icon.png',
                                name="top",
                                description="Your personal menu with shortcuts for your Issues, Merge Requests and more",
                                highlightable=False,
                                on_enter=SetUserQueryAction("%s top" % keyword)),
        ]

        return RenderResultListAction(MENU_ITEMS)

    def show_top_stories(self, load_page_number):
        import timeago

        # Get preference for what to open upon clicking an item
        open_mode = self.preferences['open_mode']
        
        # Current time to compare against (needed for '3 hours ago'-type time displays)
        # Also needed to check cached data hasn't expired
        now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)

        # Items to display later
        items = []
        
        # Index range of stories to display
        end_value = (self.SHOW_AMOUNT * load_page_number)
        start_value = end_value - (self.SHOW_AMOUNT)

        # Check if needed stories are not cached
        if len( self.cached_data["stories"] ) < end_value:
            self.load_and_cache_data(end_value)

        # Get how many minutes old the cached data is
        cache_days_old = (now-self.cached_data["cached_at"]).days
        cache_minutes_old = cache_days_old * 24 * 60

        # Get stories (Use cached data if not older than specified constant)
        if cache_minutes_old >= self.REFRESH_RATE:
            try:
                self.load_and_cache_data()
            except NameError:
                raise
        else:
            stories = self.cached_data["stories"]
        
        # Add the top 5 stories to be displayed
        for i in range(start_value, end_value):
            # TODO : Check if it is out of range, if so, load and cache the next batch.
            story = stories[i]
            logger.debug('ITEM: %s' % story)

            # Determine what url to use
            if open_mode == 'Comment Section':
                story_url = 'https://news.ycombinator.com/item?id=%d' % story.item_id
            else: # open_mode == 'URL'
                story_url = story.url

            # '3 hours ago'-type time display
            formatted_time = timeago.format(story.time, now)

            # Item info
            number_of_comments = story.descendants
            description = "%s Comments | %s | %s points | by %s " % (number_of_comments,
                                                                     formatted_time,
                                                                     story.score,
                                                                     story.by)

            # Add a last item to load the next 5 top stories
            items.append(ExtensionResultItem(icon='images/story.png',
                                name="%s" % story.title,
                                description=description,
                                highlightable=True,
                                on_enter=OpenUrlAction(story_url)))
        
        items.append(ExtensionResultItem(icon='images/next.png',
                                name='%s More Stories!' % str( self.SHOW_AMOUNT ),
                                description="The same as running 'hn %s'" % str(load_page_number + 1),
                                highlightable=True,
                                on_enter=SetUserQueryAction( 'hn %s' % str( load_page_number + 1 ) )))

        return RenderResultListAction(items)

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # Get increment page of stories to load 
        # (Eg. Page 2 - when we show 5 stories at a time - will show stories number 6-10)
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

        try:
            return extension.show_top_stories( int(page_number) )
        except NameError('ConnectionError'):
            logger.info('!!!!Displaying Error')
            return ExtensionResultItem(icon='images/story.png',
                                name="Couldn't Fetch Stories!",
                                description="Please check you Internet Connection.",
                                highlightable=False,
                                on_enter=DoNothingAction())

class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):
        return super(PreferencesEventListener, self).on_event(event, extension)

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        return super(PreferencesUpdateEventListener, self).on_event(event, extension)


if __name__ == '__main__':
    HackernewsExtension().run()