import sublime, sublime_plugin
import logging
import imp
import os.path as path

from threading import Thread  

from .plugin import tools
from .plugin import plugin_settings
from .plugin.tools import Tools
from .plugin.tools import PosStatus
from .plugin.completion import ttcn_complete

imp.reload(tools)
imp.reload(plugin_settings)
imp.reload(ttcn_complete)

completer = None
settings = None

def plugin_loaded():

    global completer
    global settings

    settings = plugin_settings.Settings()
    if settings.debug_mode:
        logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    completer = ttcn_complete.TtcnCompleter()

class TtcnComplete(sublime_plugin.EventListener):

    @staticmethod
    def on_activated_async(view):
        """Called upon activating a view. Execution in a worker thread.

        Args:
            view (sublime.View): current view

        """
        logging.debug(" on_activated_async view id %s", view.buffer_id())
        if Tools.is_valid_view(view):
            if not completer:
                return
            if completer.exist_for_view(view.buffer_id()):
                logging.debug(" view %s, already has a completer", view.buffer_id())
                return
            logging.info(" init completer for view id %s" % view.buffer_id())
            completer.init(view)
            logging.info(" init completer for view id %s doneeee" % view.buffer_id())

    @staticmethod
    def on_post_save_async(view):
        """On save. Executed in a worker thread.

        Args:
            view (sublime.View): current view

        """
        if Tools.is_valid_view(view):
            log.debug(" saving view: %s", view.buffer_id())
            if not completer:
                return
            completer.update(view)


    @staticmethod
    def on_close(view):
        """Called on closing the view.

        Args:
            view (sublime.View): current view

        """
        if Tools.is_valid_view(view):
            logging.debug(" closing view %s", view.buffer_id())
            if not completer:
                return
            completer.remove(view.buffer_id())

    def on_query_completions(self, view, prefix, locations):

        logging.debug("on_query_completions view id is %s " % view.buffer_id())
        if not Tools.is_valid_view(view):
            logging.debug(" view id %s is invalid" % view.buffer_id())
            return Tools.SHOW_DEFAULT_COMPLETIONS

        if not completer:
            logging.debug(" completer is invalid")
            return Tools.SHOW_DEFAULT_COMPLETIONS

        if completer.async_completions_ready:
            completer.async_completions_ready = False
            logging.debug(" completions result is %s", completer.completions)
            return (completer.completions)

        # Verify that character under the cursor is one allowed trigger
        pos_status = Tools.get_position_status(locations[0], view, settings)
        if pos_status == PosStatus.WRONG_TRIGGER:
            return Tools.HIDE_DEFAULT_COMPLETIONS
        if pos_status == PosStatus.COMPLETION_NOT_NEEDED:
            logging.debug(" show default completions")
            return Tools.SHOW_DEFAULT_COMPLETIONS

        logging.debug(" starting async auto_complete at pos: %s" % locations[0])
        completion_thread = Thread(
            target=completer.complete,
            args=[view, locations[0]])
        completion_thread.deamon = True
        completion_thread.start()

        logging.debug(" show default completions last")
        return Tools.HIDE_DEFAULT_COMPLETIONS


