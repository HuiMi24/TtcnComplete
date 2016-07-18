import os
import re
import logging

class BaseCompleter(object):

    ttcn_base_type = ["integer","float","charstring","bitstring","hexstring","octetstring","record","set","union","enumerated"]
    simple_types = ["boolean","char","float","integer","enumerated","charstring","octetstring","hexstring","bitstring"]

    @staticmethod
    def _get_module_name_for_tags_file(tags_file_context, type_name = None, module_name = None):
        logging.debug(" in _get_module_name_for_tags_file the type name is %s", type_name)
        return tags_file_context.get(type_name)

    @staticmethod
    def _check_type_from_module(import_modules, tags_moudles):
        logging.debug("tags_module %s", tags_moudles)
        logging.debug("import_modules %s", import_modules)
        if tags_moudles is None:
            #the last item should be current file
            return import_modules[-1]
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