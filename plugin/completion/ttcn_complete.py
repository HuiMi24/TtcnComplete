"""Contains class for completer
"""

import sublime
import re
import logging
import os
import json
import imp
import time
from ..tools import Tools
from .completions_dict_generator import CompleteDictGenerator
from .base_complete import BaseCompleter
from ..tags_file_generator import TagsFileGenerator
from . import base_complete

imp.reload(base_complete)


class TtcnCompleter(BaseCompleter):
    """A class for ttcn completions

    Attributes:
        async_completions_ready (bool): is true after async completions ready
        completions (list): current list of completions
        valid (bool): is completer valid
        flags_dict (dict): compilation flags lists for each view
    """

    async_completions_ready = False
    completions = []
    valid = False
    file_name = None
    flie_body = None
    import_modules = []
    completed_views = []
    type_tags_file_content = None
    open_folder = None
    import_item = []

    def init(self, view):
        """Initialize the completer
        """
        if not Tools.is_valid_view(view):
            return

        self.file_name = view.file_name()
        self.open_folder = view.window().folders()[0]
        self.completed_views.append(view.buffer_id())

        self.flie_body = TtcnCompleter._get_current_file_body(view)
        self.import_modules = BaseCompleter._get_import_modules(
            self.file_name, self.flie_body.split('\n'))

        if not os.path.exists(os.path.join(self.open_folder, '.type_tags')):
            logging.info(
                " the type tags file does not exist, generate new one")
            TtcnCompleter.generate_tags_file(
                view, self.open_folder, self.ttcn_base_type)
        else:
            mtime = os.path.getmtime(os.path.join(
                self.open_folder, '.type_tags'))
            current_time = time.time()
            # generate tags file every 5 minutes
            if current_time - mtime > 60 * 5:
                logging.info(" the type tags file too old, generate new one")
                TtcnCompleter.generate_tags_file(
                    view, self.open_folder, self.ttcn_base_type)

        type_tags_path = os.path.join(self.open_folder, '.type_tags')
        if not (self.open_folder and os.path.exists(type_tags_path)):
            self.type_tags_file_content = []
        else:
            logging.debug(" open type tags file %s", type_tags_path)
            with open(type_tags_path, 'r+') as f:
                self.type_tags_file_content = json.load(f)

    def remove(self, view_id):
        """remove compile flags for view

        Args:
            view_id (int): current view id
        """
        if view_id in self.completed_views:
            self.completed_views = []

    @staticmethod
    def _get_current_file_body(view):
        flie_body = view.substr(sublime.Region(0, view.size()))
        return flie_body

    # not impletment yet
    def _get_import_item(self, view):
        import_all_modules = BaseCompleter._get_import_modules(self.file_name,
                                                               self.flie_body.split(
                                                                   '\n'),
                                                               all='all')
        # remove late element, the last element is current file.
        import_all_modules.pop()
        logging.debug(" import all modules are %s", import_all_modules)
        # flie_body_lines = self.flie_body.split('\n')

    @staticmethod
    def generate_tags_file(view, root_path, ttcn_base_type):
        ttcn_pattern = '^\s*(type)\s+(%s)+\s+([a-zA-Z0-9_]+)' % '|'.join(
            ttcn_base_type)
        ttcn_gen = TagsFileGenerator(root_path,
                                     ['ttcn', 'ttcn3'])
        tags = ttcn_gen.generate_tags(ttcn_pattern)
        ttcn_gen.output_to_file(tags, '.type_tags')

    def exist_for_view(self, view_id):
        if view_id in self.completed_views:
            return True
        return False

    def complete(self, view, cursor_pos):
        (row, col) = view.rowcol(cursor_pos)

        start = time.time()
        logging.info(" started code complete for view %s", view.buffer_id())
        self.completions = TtcnCompleter._parse_completions(
            self, view, row, col)
        self.async_completions_ready = True
        TtcnCompleter._reload_completions(view)
        end = time.time()
        logging.info(" code complete done in %s seconds", end - start)

    @staticmethod
    def _reload_completions(view):
        """Ask sublime to reload the completions. Needed to update the active
        completion list when async autocompletion task has finished.

        Args:
            view (sublime.View): current_view

        """
        logging.debug(" reload completion tooltip")
        view.run_command('hide_auto_complete')
        view.run_command('auto_complete', {
            'disable_auto_insert': True,
            'api_completions_only': True,
            'next_competion_if_showing': True, })

    def _parse_completions(self, view, row, col):

        class Parser:
            @staticmethod
            def get_variable_name(flie_body, row, col):
                cur_line = flie_body[row].strip()
                logging.debug(
                    " in get_variable_name current line is %s", cur_line)
                variable_name_pattern = '(\w+)\.'
                if str:
                    m = re.findall(variable_name_pattern, cur_line)
                    if m:
                        logging.debug(" variable name is: %s" % m)
                        return m
                return []

            @staticmethod
            def get_variable_type(flie_body, row, col, variable_name):
                variable_type_pattern = '\s*(var|in|inout)?\s*(template)?\s*(\w+)\s*%s[\s{;(),]+' % variable_name
                for line in flie_body[row:row - 500:-1]:
                    m = re.search(variable_type_pattern, line)
                    if m:
                        logging.debug(" variable type is: %s" % m.group(3))
                        return m.group(3)
                return

            @staticmethod
            def _get_completions_from_file(root_path,
                                           variable_type,
                                           variables,
                                           module_name):
                for i in range(len(variables)):
                    variable = variables[i]
                    if i > 0:
                        temp = [[sub.get('type_name'), sub.get('module_name')]
                                for sub in comp_dict.get(variable_type) if sub.get('variable_name') == variable]
                        variable_type, module_name = temp[0][0], temp[0][1]
                        logging.debug("variable type is %s", variable_type)
                        logging.debug("module name is %s", module_name)
                    if module_name:
                        c = CompleteDictGenerator(module_name,
                                                  root_path,
                                                  variable_type)
                        c.parse_type()
                        comp_dict = c.completion_result
                    completions = [[sub.get('variable_name') + '\t    ' + sub.get('type_name') + ' ',
                                    sub.get('variable_name')]for sub in comp_dict.get(variable_type)]
                return completions

        completions = []
        # update file body
        self.flie_body = TtcnCompleter._get_current_file_body(view)
        flie_body_lines = self.flie_body.split('\n')

        variable_name = Parser.get_variable_name(flie_body_lines, row, col)
        logging.debug(" variables is %s", variable_name)

        if len(variable_name) == 0:
            logging.debug(" variable_name is null")
            return completions

        variable_type = Parser.get_variable_type(
            flie_body_lines, row, col, variable_name[0])
        if not variable_type:
            logging.debug(" variable_type is null")
            return completions

        tags_moudles = self._get_module_name_for_tags_file(
            self.type_tags_file_content, variable_type)
        module_name = self._check_type_from_module(
            self.import_modules, tags_moudles)

        logging.debug(" module name is %s", module_name)
        if module_name:
            logging.debug(" open folder is %s ", self.open_folder)
            completions = Parser._get_completions_from_file(self.open_folder,
                                                            variable_type,
                                                            variable_name,
                                                            module_name)
        return completions
