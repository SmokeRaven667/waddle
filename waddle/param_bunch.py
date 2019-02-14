from collections.abc import Mapping
import re
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from murmuration import kms
from murmuration import gcm
from murmuration.helpers import from_b64_str
from .bunch import Bunch
from .aws import yield_parameters


__all__ = [
    'ParamBunch',
]


dict_class = CommentedMap


def dump_yaml(x, filename):
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.explicit_start = True
    with open(filename, 'w') as f:
        yaml.dump(x, f)


class ParamBunch(Bunch):
    def __init__(self, values=None, prefix=None):
        super(ParamBunch, self).__init__(values)
        super(ParamBunch, self)._set('original_values', values)
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

    def encryption_key(self, decrypt=True):
        encryption_key = self.get('meta.encryption_key')
        if encryption_key and decrypt:
            region = self.get('meta.region')
            profile = self.get('meta.profile')
            encryption_key = from_b64_str(encryption_key)
            encryption_key = kms.decrypt_bytes(encryption_key, region, profile)
        return encryption_key

    @staticmethod
    def try_decrypt(value, encryption_key, decrypt):
        if encryption_key and decrypt and isinstance(value, str):
            try:
                value = gcm.decrypt(value, encryption_key)
            except ValueError:
                pass
        return value

    def from_file(self, filename, decrypt=True):
        with open(filename, 'r', encoding='utf-8') as f:
            yaml = YAML()
            data = yaml.load(f)
        super(ParamBunch, self)._set('original_values', data)
        values = []
        for key, value in ParamBunch._traverse(data):
            if key in ['values', 'original_values' ]:
                raise KeyError('`values` is not a valid key name')
            elif key.startswith('meta.'):
                self[key] = value
            else:
                values.append((key, value))
        encryption_key = self.encryption_key(decrypt)
        for key, value in values:
            self[key] = ParamBunch.try_decrypt(value, encryption_key, decrypt)

    def load(self, prefix=None, filename=None, decrypt=True):
        if prefix:
            self.from_aws(prefix)
        if filename:
            self.from_file(filename, decrypt)

    def from_aws(self, prefix):
        if not prefix.startswith('/'):
            prefix = f'/{prefix}'
        prefix = prefix.replace('.', '/')
        for key, value in yield_parameters(prefix):
            self[key] = value

    def original_value(self, key):
        data = self.original_values
        if key in data:
            return data, key, data[key]
        pieces = key.split('.')
        for x in pieces[:-1]:
            data = data[x]
        key = pieces[-1]
        return data, key, data[key]

    def original_parent(self, key):
        data = self.original_values
        pieces = key.split('.')
        try:
            for x in pieces[:-1]:
                data = data[x]
            return data, pieces[-1]
        except (KeyError, TypeError):
            return self.original_values, key

    def fill_back(self):
        updated_values = []
        new_values = []
        for key, value in self.items():
            try:
                parent, key, original_value = self.original_value(key)
                if value != original_value:
                    updated_values.append((parent, key, value))
            except (KeyError, TypeError):
                new_values.append((key, value))
        self.handle_updates(updated_values)
        self.handle_new(new_values)

    def handle_updates(self, updated_values):
        # pylint: disable=access-member-before-definition
        for parent, key, value in updated_values:
            parent[key] = value
        if self.original_values is None:
            self.original_values = dict_class()

    def handle_new(self, new_values):
        for key, value in new_values:
            parent, x = self.original_parent(key)
            parent[x] = value

    def save(self, filename):
        self.fill_back()
        dump_yaml(self.original_values, filename)
