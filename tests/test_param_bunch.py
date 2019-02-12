import os
from unittest import TestCase
import pytest
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
        self.assertEqual(b.meta.namespace, 'test.waddle')

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
        self.assertEqual(b.meta.namespace, 'test.waddle2')
        self.assertEqual(b.meta.kms_key, 'dev')

    def test_items(self):
        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
        })
        b.meta.namespace = 'test.waddle'
        values = {
            '/test/waddle/a/b/cat': 'cody',
            '/test/waddle/a/b/dog': 'peanut',

        }
        for key, value in b.aws_items():
            self.assertEqual(values[key], value)

    def test_file_items(self):
        b = ParamBunch({
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
        })
        b.meta.namespace = 'test.waddle'
        values = {
            'a.b.cat': 'cody',
            'a.b.dog': 'peanut',
            'meta.namespace': 'test.waddle',
        }
        n = 0
        for key, value in b.file_items():
            n += 1
            self.assertEqual(values[key], value)
        self.assertEqual(n, len(values))

    def test_to_dict(self):
        data = {
            'a': {
                'b': {
                    'cat': 'cody',
                    'dog': 'peanut',
                },
            },
            'meta': {
                'namespace': 'test.waddle',
                'kms_key': 'dev',
            }
        }
        b = ParamBunch(data)
        self.assertEqual(b.to_dict(), data)

    def test_error_config(self):
        b = ParamBunch()
        with pytest.raises(KeyError) as exc_info:
            b.from_file('tests/conf/error.yml')
        self.assertIn('`values`', exc_info.value.args[0])

    def test_nested_config(self):
        b = ParamBunch()
        b.load(filename='tests/conf/nested.yml')
        self.assertIn('cody', b.waddle.cats)
        self.assertIn('olive', b.waddle.dogs)

    def test_flat_config(self):
        b = ParamBunch()
        b.load(filename='tests/conf/flat.yml')
        self.assertIn('cody', b.waddle.cats)
        self.assertIn('olive', b.waddle.dogs)
        self.assertEqual(b.meta.namespace, 'test')
        self.assertEqual(b.meta.kms_key, 'dev')

    def test_save_flat(self):
        b = ParamBunch()
        b.waddle.cats = [
            'cody',
            'taylor',
            'jinx',
            'padme',
        ]
        b.waddle.dogs = [
            'peanut',
            'olive',
        ]
        b.meta.namespace = 'test'
        b.meta.kms_key = 'dev'
        filename = 'tests/conf/save_flat.yml'
        b.save(filename, flat=True, nested=True)
        with open(filename, 'r') as f:
            actual = f.read()
        with open('tests/conf/expected_save_flat.yml') as f:
            expected = f.read()
        self.assertEqual(actual, expected)
        os.remove(filename)

    def test_save_nested(self):
        b = ParamBunch()
        b.waddle.cats = [
            'cody',
            'taylor',
            'jinx',
            'padme',
        ]
        b.waddle.dogs = [
            'peanut',
            'olive',
        ]
        b.meta.namespace = 'test'
        b.meta.kms_key = 'dev'
        filename = 'tests/conf/save_nested.yml'
        b.save(filename, nested=True)
        with open(filename, 'r') as f:
            actual = f.read()
        with open('tests/conf/nested.yml') as f:
            expected = f.read()
        self.assertEqual(actual, expected)
        os.remove(filename)
