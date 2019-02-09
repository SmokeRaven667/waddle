from collections.abc import Mapping
import yaml
from .bunch import Bunch
from .bunch import wrap
from .aws import yield_parameters


__all__ = [
    'ParamBunch',
]


class ParamBunch(Bunch):
    def __init__(self, values=None, prefix=None):
        super(ParamBunch, self).__init__(values)
        meta = self.values.get('meta')
        if meta is not None:
            del values['meta']
        else:
            meta = {}
        super(ParamBunch, self)._set('meta', wrap(meta))
        if prefix:
            self.meta.namespace = prefix
            self.from_aws(prefix)

    @property
    def namespace(self):
        return self.meta.get('namespace')

    @property
    def kms_key(self):
        return self.meta.get('kms_key', False)

    def aws_items(self, values=None, prefix=None):
        prefix = prefix or [ '', self.namespace ]
        for key, value in self.items(values, prefix):
            key = key.replace('.', '/')
            yield key, value

    def file_items(self, values=None, prefix=None):
        yield from self.items(values, prefix)
        yield from self.meta.items(prefix=['meta'])

    def to_dict(self):
        result = super(ParamBunch, self).to_dict()
        result['meta'] = self.meta.values
        return result

    @staticmethod
    def _traverse(d, prefix=None):
        prefix = prefix or []
        for key, value in d.items():
            if isinstance(value, Mapping):
                yield from ParamBunch._traverse(value, prefix + [ key ])
            else:
                yield '.'.join(prefix + [ key ]), value

    def _handle_meta(self, data):
        meta = data.pop('meta', None)
        if meta:
            self.meta = meta

    def _handle_meta_value(self, key, value):
        self.meta[key] = value

    def from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
            self._handle_meta(data)
            for key, value in ParamBunch._traverse(data):
                if key == 'values':
                    raise KeyError('`values` is not a valid key name')
                elif key.startswith('meta.'):
                    self._handle_meta_value(key[5:], value)
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
