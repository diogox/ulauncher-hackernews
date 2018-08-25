class Preferences:

    KEYWORD = ''
    OPEN_MODE = ''
    CACHE_INCREMENT = ''
    CACHE_REFRESH_RATE = ''
    ITEM_AMOUNT = ''

    def set_preferences(self, preferences):
        # Save preferences reference
        self.source = preferences

        # Save values as members
        self.load(preferences)
        
    def load(self, preferences):
        """
        Saves the preference values as 
        members of the class
        """
        self.KEYWORD = preferences["keyword"]
        self.OPEN_MODE = preferences["open_mode"]
        self.CACHE_REFRESH_RATE = int( preferences["cache_refresh_rate"] )
        self.ITEM_AMOUNT = int( preferences["item_amount"] )

        if self.CACHE_REFRESH_RATE == 0:
            # If there is no cache, there's no need to cache pages ahead
            # Only load the current one
            self.CACHE_INCREMENT = 1
        else:
            self.CACHE_INCREMENT = int( preferences["cache_increment"] )


    def update(self):
        """ 
        Updates the internal reference to 
        the values in the preferences 
        """
        self.load( self.source )