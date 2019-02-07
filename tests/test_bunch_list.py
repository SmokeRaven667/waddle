import pickle
from unittest import TestCase
from stork.bunch import BunchList


__all__ = [
    'BunchListTest',
]


class BunchListTest(TestCase):
    def test_repr(self):
        a = BunchList([ 1, 2, 3 ])
        self.assertEqual(f'{a}', '[1, 2, 3]')
        a = BunchList((1, 2, 3))
        self.assertEqual(f'{a}', '[1, 2, 3]')

    def test_eq(self):
        values = [ 1, 2, 3 ]
        a = BunchList(values)
        b = BunchList(values)
        c = BunchList([1, 2, 3, 4])
        self.assertTrue(a == values)
        self.assertTrue(b == a)
        self.assertTrue(b != c)
        self.assertFalse(b != a)

    def test_indexing(self):
        values = [ 1, 2, 3 ]
        a = BunchList(values)
        b = BunchList([2, 3])
        self.assertEqual(a[0], 1)
        self.assertEqual(a[-2], 2)
        self.assertEqual(a[1:3], b)
        a[-1] = 0
        self.assertEqual(a[-1], 0)

    def test_iter(self):
        values = [ 1, 2, 3 ]
        a = BunchList(values)
        for n, x in enumerate(a, 1):
            self.assertEqual(n, x)

    def test_len(self):
        values = [ 1, 2 ]
        a = BunchList(values)
        self.assertEqual(len(a), 2)

    def test_zero(self):
        a = BunchList([])
        b = BunchList([1, 2, 3])
        self.assertTrue(b)
        self.assertFalse(a)

    def test_pickle(self):
        b = BunchList([1, 2, 3])
        value = pickle.dumps(b)
        value = pickle.loads(value)
        self.assertEqual(b, value)

    def test_getattr(self):
        b = BunchList([1, 2, 3])
        self.assertEqual(getattr(b, 'cat', 'cody'), 'cody')
