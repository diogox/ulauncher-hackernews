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

logger = logging.getLogger(__name__)

class HackernewsExtension(Extension):

    def __init__(self):
        super(HackernewsExtension, self).__init__()

        # Subscribe to events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        #self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def show_main_menu(self):
        items = []
        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        return super(KeywordQueryEventListener, self).on_event(event, extension)

class PreferencesEventListener(EventListener):

    # Activates when the application first reads the preferences on launch
    def on_event(self, event, extension):
        return super(PreferencesEventListener, self).on_event(event, extension)

class PreferencesUpdateEventListener(EventListener):
    
    def on_event(self, event, extension):
        return super(PreferencesUpdateEventListener, self).on_event(event, extension)


if __name__ == '__main__':
    HackernewsExtension().run()