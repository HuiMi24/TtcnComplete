import re
import os
import logging
import json

class TagsFileGenerator(object):
    """docstring for TagsFileGenerator"""
    def __init__(self, root_path, file_extension):
        self.root_path = root_path
        self.files = []
        self.file_extension = '|'.join(file_extension) + "$"
        logging.debug(" file extension is %s", self.file_extension)
        self._find()

    def _find(self):
        for root, dirs, files in os.walk(self.root_path):
            for name in files:
                if re.search(self.file_extension, name):
                    self.files.append(os.path.join(root, name))
        return

    def generate_tags(self, pattern):
        tags = dict()
        for file in self.files:
            if os.path.exists(file):
                with open(file, encoding="ISO-8859-1") as f:
                    file_content =  f.readlines()
                for line in file_content:
                    m = re.match(pattern, line)
                    if m:
                        logging.debug(" generate tags for file %s", file)
                        if tags.get(m.group(3)) is None:
                            tags[m.group(3)] = []
                        tags[m.group(3)].append(str(file))
        return tags

    def output_to_file(self, tags, tags_file_name):
        with open(os.path.join(self.root_path, tags_file_name), 'w+') as f:
            json.dump(tags, f)


