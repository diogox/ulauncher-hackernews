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
        self.CACHE_INCREMENT = int( preferences["cache_increment"] )
        self.CACHE_REFRESH_RATE = int( preferences["cache_refresh_rate"] )
        self.ITEM_AMOUNT = int( preferences["item_amount"] )


    def update(self):
        """ 
        Updates the internal reference to 
        the values in the preferences 
        """
        self.load( self.source )