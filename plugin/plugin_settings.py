import sublime
import logging

from .tools import PKG_NAME

class Settings(object):
    """
    class that encapsulates sublime settings
    sublime_settings (sublime.settings): linke to sublime text setting dict
    triggers (string[]): triggers that trigger autocompletion
    debug_mode (bool): debug flag
    """
    sublime_settings = None
    triggers = None
    debug_mode = None

    def __init__(self):
        """
        Initialize the class
        """
        self.load_settings()
        if not self.is_valid():
            logging.critical(" Could not load settings!")
            logging.critical(" NO AUTOCOMPLETE WILL BE AVAILABLE")
            return

    def load_settings(self):
        """
        Load settings from sublime dictionary to internal variables
        """
        self.sublime_settings = sublime.load_settings(PKG_NAME + ".sublime-settings")
        self.debug_mode = self.sublime_settings.get("debug_mode")
        self.triggers = self.sublime_settings.get("triggers")

    def is_valid(self):
        """Check settings validity. If any of the settings is None the settings
        are not valid.

        Returns:
            bool: validity of settings
        """
        if self.sublime_settings is None:
            logging.critical(" no sublime_settings found")
            return False
        if self.debug_mode is None:
            logging.critical(" no debug_mode found")
            return False
        if self.triggers is None:
            logging.critical(" no triggers found")
            return False
        return True