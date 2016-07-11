"""Contains class for completer

Attributes:
    log (logging.Logger): logger for this module

"""

import sublime
import re
import logging
import os
import json
from ..tools import Tools
from .completions_dict_generator import CompleteDictGenerator
from .base_complete import BaseCompleter


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
    import_modules = []
    tags_file_content = None
    completed_views = []
    type_tags_file_content = None

    def init(self, view):
        """Initialize the completer
        """
        if not Tools.is_valid_view(view):
            return

        self.file_name = view.file_name()

        tags_path = view.window().folders()[0] + '/' + '.tags'
        if not (view.window().folders() and os.path.exists(tags_path)):
            tags_file_content = []
        else:
            f = open(tags_path, 'r+')
            self.tags_file_content = f.readlines()
            f.close()

        type_tags_path = view.window().folders()[0] + '/' + '.type_tags'
        if not (view.window().folders() and os.path.exists(type_tags_path)):
            type_tags_file_content = []
        else:
            f = open(tags_path, 'r+')
            self.type_tags_file_content = f.readlines()
            f.close()
        self.completed_views.append(view.buffer_id())

    def exist_for_view(self, view_id):
        if view_id in self.completed_views:
            return True
        return False

    def complete(self, view, cursor_pos):
        flie_body = view.substr(sublime.Region(0, view.size()))
        (row, col) = view.rowcol(cursor_pos)

        self.completions = TtcnCompleter._parse_completions(self, view, flie_body, row, col)
        self.async_completions_ready = True
        TtcnCompleter._reload_completions(view)

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

    def _parse_completions(self, view, flie_body, row, col):
        class Parser:
            @staticmethod
            def get_variable_name(flie_body, row, col):
                cur_line = flie_body[row].strip()
                variable_name_pattern = '([a-zA-Z0-9_]*)\.'
                if str:
                    m = re.findall(variable_name_pattern, cur_line)
                    if m:
                        logging.debug(" variable name is: %s" % m)
                        return m
                return []

            @staticmethod
            def get_variable_type(flie_body, row, col, variable_name):
                variable_type_pattern = '^\s*(var)?\s*(template)?\s*(\w+)\s*'+ variable_name
                for line in flie_body[row::-1]:
                    m = re.match(variable_type_pattern, line)
                    if m:
                        logging.debug(" variable type is: %s" % m.group(3))
                        return m.group(3)
                return

            @staticmethod
            def get_import_modules(flie_body):
                import_pattern = re.compile('\s*import\s*from\s*(\w+)')
                import_modules = []
                for line in flie_body:
                    m = re.match(import_pattern, line)
                    if m:
                        #logging.debug(" import module: %s", m.group(1))
                        import_modules.append(m.group(1))
                return import_modules

            @staticmethod
            def _get_completions_from_file(root_path, variable_type, variables,module_name):
                for i in range(len(variables)):
                    variable = variables[i]
                    if i > 0:
                        temp = [ [sub.get('type_name'), sub.get('module_name')] \
                            for sub in comp_dict.get(variable_type) if sub.get('variable_name') == variable]
                        variable_type = temp[0][0]
                        module_name = temp[0][1]
                        logging.debug("variable type is %s", variable_type)
                        logging.debug("module name is %s", module_name)
                    if module_name:
                        c = CompleteDictGenerator(module_name,
                                                  root_path,
                                                  variable_type)
                        c.parse_type()
                        comp_dict = c.completion_result
                    completions = [ [sub.get('variable_name') + '\t    ' + sub.get('type_name'),\
                                     sub.get('variable_name')]for sub in comp_dict.get(variable_type)]
                return completions


        completions = []
        flie_body_lines = flie_body.split('\n')
        variable_name = Parser.get_variable_name(flie_body_lines, row, col)
        if len(variable_name) == 0:
            logging.debug(" variable_name is null")
            return completions
        variable_type = Parser.get_variable_type(flie_body_lines, row, col, variable_name[0])
        if not variable_type:
            logging.debug(" variable_type is null")
            return completions
        import_modules = Parser.get_import_modules(flie_body_lines)
        tags_moudles = self._get_module_name_for_tags_file(self.type_tags_file_content, variable_type)
        module_name = self._check_type_from_module(import_modules, tags_moudles)
        logging.debug(" module name is %s", module_name)
        if module_name:
            completions = Parser._get_completions_from_file(view.window().folders()[0],
                                                        variable_type,
                                                        variable_name,
                                                        module_name)
        return completions
