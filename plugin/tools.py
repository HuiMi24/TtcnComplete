"""This module contains various tools

Attributes:
    PKG_NAME (str): this package name
"""

import os.path as path
import sublime
import re
import logging

PKG_NAME = path.basename(path.dirname(path.dirname(__file__)))


class PosStatus:
    """ Enum class for position status

    Attributes:
        COMPLETION_NEEDED (int): completion needed
        COMPLETION_NOT_NEEDED (int): completion not needed
        WRONG_TRIGGER (int): trigger is wrong
    """
    COMPLETION_NEEDED = 0
    COMPLETION_NOT_NEEDED = 1
    WRONG_TRIGGER = 2


class Tools(object):
    """docstring for Tools"""

    syntax_regex = re.compile("\/([^\/]+)\.(?:tmLanguage|sublime-syntax)")

    valid_extensions = [".ttcn", "ttcn3"]
    valid_syntax = ["ttcn3"]

    SHOW_DEFAULT_COMPLETIONS = None
    HIDE_DEFAULT_COMPLETIONS = ([], sublime.INHIBIT_WORD_COMPLETIONS |
                                sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    @staticmethod
    def get_view_syntax(view):
        """Get syntax from view description

        Args:
            view (sublime.View): Current view

        Returns:
            str: syntax, e.g. "ttcn"
        """
        syntax = re.findall(Tools.syntax_regex,
                            view.settings().get('syntax'))
        if len(syntax) > 0:
            return syntax[0]
        return None

    @staticmethod
    def has_valid_syntax(view):
        """Check if syntax is valid for this plugin

        Args:
            view (sublime.View): current view

        Returns:
            bool: True if valid, False otherwise
        """
        syntax = Tools.get_view_syntax(view)
        if syntax in Tools.valid_syntax:
            logging.debug("%s file has valid syntax: %s" %
                          (view.file_name(), syntax))
            return True
        logging.debug("%s file has unsupported syntax: %s" %
                      (view.file_name(), syntax))
        return False

    @staticmethod
    def is_valid_view(view):
        """
        Check whether the given view is one we want to handle
        Args:
            view (sublime.view): view to check
        Returns:
            bool: True if we want to handle this view, False otherwise
        """
        if not view:
            return False
        if not view.file_name():
            return False
        if not Tools.has_valid_syntax(view):
            return False
        if view.is_scratch():
            return False
        return True

    @staticmethod
    def get_position_status(point, view, settings):
        """Check if the cursor focuses a valid trigger

        Args:
            point (int): position of the cursor in the file as defined by subl
            view (sublime.View): current view
            settings (TYPE): Description

        Returns:
            PosStatus: statuf for this position
        """
        trigger_length = 1
        word_on_the_left = view.substr(view.word(point - trigger_length))
        if word_on_the_left.isdigit():
            log.debug(" trying to autocomplete digit, are we? Not allowed.")
            return PosStatus.WRONG_TRIGGER

        # slightly counterintuitive `view.substr` returns ONE character
        # to the right of given point.
        curr_char = view.substr(point - trigger_length)
        wrong_trigger_found = False
        for trigger in settings.triggers:
            if curr_char == trigger[-1]:
                trigger_length = len(trigger)
                prev_char = view.substr(point - trigger_length)
                if prev_char == trigger[0]:
                    logging.debug(" prev_char is %s" % prev_char)
                    logging.debug(" matched trigger %s" % trigger)
                    return PosStatus.COMPLETION_NEEDED
                else:
                    logging.debug(" wrong trigger %s%s" %
                                  (prev_char, curr_char))
                    wrong_trigger_found = True
        if wrong_trigger_found:
            logging.debug(" wrong trigger fired")
            return PosStatus.WRONG_TRIGGER

        logging.debug(" no completions needed")
        return PosStatus.COMPLETION_NOT_NEEDED
