from collections.abc import Mapping
from collections import OrderedDict
import copy
import re
import yaml
from yaml import Dumper
from .bunch import Bunch
from .aws import yield_parameters


__all__ = [
    'ParamBunch',
]


dict_class = OrderedDict


def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())


class YamlDumper(Dumper):
    # pylint: disable=too-many-ancestors,too-many-arguments
    def __init__(
            self, stream,
            default_style=None, default_flow_style=None,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None):
        if default_flow_style is None:
            default_flow_style = False
        if line_break is None:
            line_break = '\n'
        if indent is None:
            indent = 2
        if explicit_start is None:
            explicit_start = True
        super(YamlDumper, self).__init__(
            stream, default_style, default_flow_style, canonical, indent,
            width, allow_unicode, line_break, encoding, explicit_start,
            explicit_end, version, tags)
        self.add_representer(dict_class, dict_representer)

    def increase_indent(self, flow=False, indentless=False):
        return super(YamlDumper, self).increase_indent(flow, False)


def dump_yaml(x, filename):
    with open(filename, 'w') as f:
        yaml.dump(x, f, Dumper=YamlDumper)


class ParamBunch(Bunch):
    def __init__(self, values=None, prefix=None):
        super(ParamBunch, self).__init__(values)
        if prefix:
            self.meta.namespace = prefix
            self.from_aws(prefix)

    def aws_items(self, values=None, prefix=None):
        prefix = prefix or [ '', self.meta.namespace ]
        for key, value in self.items(values, prefix):
            if '.meta.' in key:
                continue
            key = key.replace('.', '/')
            yield key, value

    def file_items(self, values=None, prefix=None):
        meta_prefix = re.compile(r'^\.?meta\.')
        for key, value in self.items(values, prefix):
            if meta_prefix.match(key):
                continue
            yield key, value
        yield from self.items(values=self.meta.values, prefix=[ 'meta' ])

    def to_dict(self):
        result = super(ParamBunch, self).to_dict()
        return result

    @staticmethod
    def _traverse(d, prefix=None):
        prefix = prefix or []
        for key, value in d.items():
            if isinstance(value, Mapping):
                yield from ParamBunch._traverse(value, prefix + [ key ])
            else:
                yield '.'.join(prefix + [ key ]), value

    def from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
            for key, value in ParamBunch._traverse(data):
                if key == 'values':
                    raise KeyError('`values` is not a valid key name')
                else:
                    self[key] = value

    def load(self, prefix=None, filename=None):
        if prefix:
            self.from_aws(prefix)
        if filename:
            self.from_file(filename)

    def from_aws(self, prefix):
        if not prefix.startswith('/'):
            prefix = f'/{prefix}'
        prefix = prefix.replace('.', '/')
        for key, value in yield_parameters(prefix):
            self[key] = value

    def save_flat(self, filename):
        x = dict_class()
        for key, value in self.items():
            x[key] = value
        dump_yaml(x, filename)

    def save_nested(self, filename):
        x = copy.deepcopy(self.values)
        dump_yaml(x, filename)

    def save(self, filename, flat=False, nested=False):
        if nested and flat:
            nested = False
        if nested:
            self.save_nested(filename)
        else:
            self.save_flat(filename)
