from .bunch import Bunch
from .bunch import wrap


__all__ = [
    'ParamBunch',
]


class ParamBunch(Bunch):
    def __init__(self, values=None):
        super(ParamBunch, self).__init__(values)
        meta = values.get('meta')
        if meta is not None:
            del values['meta']
        else:
            meta = {}
        super(ParamBunch, self)._set('meta', wrap(meta))

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
