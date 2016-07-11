import os
import re

class BaseCompleter(object):

    @staticmethod
    def _get_module_name_for_tags_file(tags_file_context, type_name):
        type_pattern = '\s*%s\s+([\w/\.]+)' % type_name
        res = []
        for line in tags_file_context:
            m = re.match(type_pattern,line)
            if m:
                res.append( m.group(1))
        return res

    @staticmethod
    def _check_type_from_module(import_modules, tags_moudles):
        for tags_module in tags_moudles:
            for import_module in import_modules:
                if import_module == os.path.basename(tags_module).split('.')[0]:
                    return tags_module
        return