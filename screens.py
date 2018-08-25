from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import utils

class Screens:

    def set_preferences(self, preferences):
        # Keep preferences
        self.preferences = preferences

    def render_main_screen(self):
        # Either menu or top stories, depending on the preferences
        pass

    def render_menu(self):
        pass

    def render_top_stories(self, stories, page_number):
        import timeago

        items = []
        for story in stories:
            # Determine what url to use
            if (self.preferences.OPEN_MODE):
                url = 'https://news.ycombinator.com/item?id=%d' % story.item_id
            else: # open_mode == 'URL'
                url = story.url
            
            # '3 hours ago'-type time display
            formatted_time = timeago.format(story.time, utils.get_current_time())

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
                                on_enter=OpenUrlAction(url)))

        # Item to get to the neext page
        items.append(ExtensionResultItem(icon='images/next.png',
                                name='Load Next Page!',
                                description="The same as running 'hn %s'" % str( page_number + 1 ),
                                highlightable=True,
                                on_enter=SetUserQueryAction( 'hn %s' % str( page_number + 1 ) )))

        return items