from .bunch import Bunch


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
        super(ParamBunch, self)._set('meta', meta)

    @property
    def namespace(self):
        return self.meta.get('namespace')

    @property
    def kms_key(self):
        return self.meta.get('kms_key', False)

    def items(self, values=None, prefix=None):
        prefix = prefix or [ '', self.namespace ]
        for key, value in super(ParamBunch, self).items(values, prefix):
            key = key.replace('.', '/')
            yield key, value
