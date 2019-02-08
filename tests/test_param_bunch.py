from unittest import TestCase
from waddle import ParamBunch


__all__ = [
    'ParamBunchTest',
]


class ParamBunchTest(TestCase):
    def test_constructor(self):
        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
            'meta': {
                'namespace': 'test.waddle',
            }
        })
        self.assertEqual(b.namespace, 'test.waddle')
        self.assertEqual(b.kms_key, False)

        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
            'meta': {
                'namespace': 'test.waddle2',
                'kms_key': 'dev',
            }
        })
        self.assertEqual(b.namespace, 'test.waddle2')
        self.assertEqual(b.kms_key, 'dev')

        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
        })
        self.assertEqual(b.namespace, None)
        self.assertEqual(b.kms_key, False)

    def test_items(self):
        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
            'meta': {
                'namespace': 'test.waddle',
            }
        })
        values = {
            '/test/waddle/a/b/cat': 'cody',
            '/test/waddle/a/b/dog': 'peanut',

        }
        for key, value in b.items():
            self.assertEqual(values[key], value)
