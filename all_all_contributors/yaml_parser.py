"""
Class to safely parse yaml to string and vice versa
"""

from io import StringIO

import ruamel.yaml


def represent_none(self, data):
    return self.represent_scalar("tag:yaml.org,2002:null", "null")


class YamlParser:
    def __init__(self):
        self.yaml = ruamel.yaml.YAML()
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.allow_duplicate_keys = True
        self.yaml.explicit_start = False
        self.yaml.preserve_quotes = True
        self.yaml.representer.add_representer(type(None), represent_none)

    def object_to_yaml_str(self, obj, options={}):
        string_stream = StringIO()
        self.yaml.dump(obj, string_stream, **options)
        output_str = string_stream.getvalue()
        string_stream.close()

        return output_str

    def yaml_string_to_object(self, string, options={}):
        return self.yaml.load(string, **options)
