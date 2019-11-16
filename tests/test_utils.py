from unittest import TestCase
from waddle import load_config


__all__ = [
    'TestUtils',
]


class TestUtils(TestCase):
    def test_cascade(self):
        conf = load_config('tests/conf/base.yml', 'tests/conf/mid.yml')
        self.assertEqual(conf.parent.key, 'mid_value')

    def test_not_exists(self):
        conf = load_config('tests/conf/base.yml', 'tests/conf/dne.yml')
        self.assertEqual(conf.parent.key, 'base_value')
