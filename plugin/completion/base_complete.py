import os
import re
import logging

class BaseCompleter(object):

    ttcn_base_type = ["integer","float","charstring","bitstring","hexstring","octetstring","record","set","union","enumerated"]
    simple_types = ["boolean","char","float","integer","enumerated","charstring","octetstring","hexstring","bitstring"]

    @staticmethod
    def _get_module_name_for_tags_file(tags_file_context, type_name):
        type_pattern = '^\s*%s\s+([\w/\.:\\\\ ]+)' % type_name
        logging.debug("_get_module_name_for_tags_file %s", type_pattern )
        res = []
        for line in tags_file_context:
            m = re.search(type_pattern, line)
            if m:
                res.append( m.group(1))
        return res

    @staticmethod
    def _check_type_from_module(import_modules, tags_moudles):
        logging.debug("tags_module %s", tags_moudles)
        logging.debug("import_modules %s", import_modules)
        for tags_module in tags_moudles:
            for import_module in import_modules:
                if import_module == os.path.basename(tags_module).split('.')[0]:
                    return tags_module
        return

    @staticmethod
    def _get_import_modules(file_name, flie_body):
        import_pattern = re.compile('\s*import\s*from\s*(\w+)')
        import_modules = []
        for line in flie_body:
            m = re.match(import_pattern, line)
            if m:
                #logging.debug(" import module: %s", m.group(1))
                import_modules.append(m.group(1))
        #the last item is current module
        import_modules.append(os.path.basename(file_name.split('.')[0]))
        return import_modules