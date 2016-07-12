import re
import os
import logging

class TagsFileGenerator(object):
    """docstring for TagsFileGenerator"""
    def __init__(self, root_path, file_extension):
        self.root_path = root_path
        self.files = []
        self.file_extension = file_extension
        self._find()

    def _find(self):
        for root, dirs, files in os.walk(self.root_path):
            for name in files:
                if name.endswith(self.file_extension):
                    self.files.append(os.path.join(root, name))
        return

    def generate_tags(self, pattern):
        tags = []
        for file in self.files:
            logging.debug(" generate_tags open file %s", file)
            if os.path.exists(file):
                with open(file, encoding="ISO-8859-1") as f:
                    file_content =  f.readlines()
                for line in file_content:
                    m = re.match(pattern, line)
                    if m:
                        #logging.debug(" generate tags for file %s", file)
                        res = '{:s}\t{:s}\t/^    {:s}$/;"   r\n'.format(m.group(3), str(file), m.group())
                        tags.append(res)
        return tags

    def output_to_file(self, tags, tags_file_name):
        f = open(os.path.join(self.root_path, tags_file_name), 'w+')
        for line in tags:
            f.write(line)
        f.close()


