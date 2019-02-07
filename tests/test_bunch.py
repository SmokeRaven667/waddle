import os
import pickle
from unittest import TestCase
import pytest
from waddle.bunch import Bunch


__all__ = [
    'Bunch',
]


class BunchTest(TestCase):
    def test_can_create(self):
        b = Bunch()
        self.assertIsNotNone(b)

    def test_get_item(self):
        a = {
            'b': {
                'c': True,
                'd': False,
            }
        }
        b = Bunch({ 'a': a, })
        self.assertTrue(b['a.b.c'])
        self.assertFalse(b['a.b.d'])
        self.assertIsInstance(b['a'], Bunch)
        self.assertIsNone(b['cody'])
        self.assertIsNone(b['cats.cody'])

    def test_set_item(self):
        b = Bunch()
        b['a.b.c'] = True
        b['a.b.d'] = False
        self.assertTrue(b['a.b.c'])
        self.assertFalse(b['a.b.d'])
        self.assertIsInstance(b['a'], Bunch)
        self.assertIsNone(b['cody'])

    def test_get(self):
        b = Bunch()
        b['a.b.c'] = True
        b['a.b.d'] = False
        self.assertTrue(b.get('a.b.c'))
        self.assertFalse(b.get('a.b.d'))
        self.assertIsInstance(b.get('a'), Bunch)
        self.assertEqual(b.get('cat.cody', 2), 2)

    def test_contains(self):
        b = Bunch()
        b['a.b.c'] = True
        self.assertTrue('a.b.c' in b)
        self.assertFalse('a.d' in b)
        self.assertFalse('hello.cody' in b)

    def test_setdefault(self):
        b = Bunch()
        self.assertTrue(b.setdefault('a.b.c', True))
        self.assertTrue(b.setdefault('a.b.c', False))
        self.assertEqual(b.values, { 'a': {
            'b': {
                'c': True,
            }
        } })

    def test_zero(self):
        b = Bunch()
        self.assertFalse(b)
        b['a.cody'] = 'cat'
        self.assertTrue(b)

    def test_dir(self):
        b = Bunch({
            'will': {
                'cats': {
                    'cody': 1,
                    'jinx': 1,
                    'padme': 1,
                }
            },
            'yw': {
                'taylor': 1,
            },
            'frank': {
                'strays': 3,
            }
        })
        self.assertIn('yw', b.__dir__())
        self.assertIn('frank', b.__dir__())
        self.assertNotIn('yuki', b.__dir__())

    def test_equals(self):
        a = Bunch()
        b = Bunch()
        c = Bunch()
        a['peter.dogs'] = [ 'olive' ]
        b['peter.dogs'] = [ 'olive' ]
        c['justin.dogs'] = [ 'peanut' ]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(b, c)

    def test_repr(self):
        a = Bunch()
        a['peter.dogs.olive'] = '@olivetoroam'
        self.assertEqual(
            repr(a),
            "{'peter': {'dogs': {'olive': '@olivetoroam'}}}")
        a = Bunch()
        key = 'some.really.long.key.that.is.longer.than.sixty.characters'
        a[key] = 'hello'
        self.assertEqual(
            repr(a),
            "{'some': {'really': {'long': {'key': {'that': {'is': {'longe...}")

    def test_set_state(self):
        a = Bunch()
        a['peter.dogs'] = [ 'olive' ]
        a['justin.dogs'] = [ 'peanut' ]
        b = pickle.dumps(a)
        c = pickle.loads(b)
        self.assertIn('olive', c['peter.dogs'])
        self.assertIn('peanut', c['justin.dogs'])

    def test_get_attr(self):
        a = Bunch()
        self.assertEqual(a.b.e, {})
        a = {
            'b': {
                'c': True,
                'd': False,
            }
        }
        a = Bunch(a)
        self.assertTrue(a.b.c)
        self.assertFalse(a.b.d)

    def test_set_attr(self):
        a = Bunch()
        a.b.c = True
        a.b.d = False
        self.assertTrue(a.b.c)
        self.assertFalse(a.b.d)

    def test_del_item(self):
        a = Bunch()
        a.b.c = True
        a.b.d = False
        del a['b.c']
        del a['hello.cody']
        self.assertIn('b', a)
        self.assertIn('b.d', a)
        self.assertNotIn('b.c', a)

    def test_del_attr(self):
        a = Bunch()
        a.b.c = True
        a.b.d = False
        del a.b.d
        self.assertIn('b', a)
        self.assertIn('b.c', a)
        self.assertNotIn('b.d', a)
        with pytest.raises(AttributeError):
            del a.cody

    def test_env(self):
        a = Bunch()
        value = 'test.example.com'
        a.ftp.host = value
        env = a.env()
        os.environ['FTP_PASSWORD'] = 'secret'
        self.assertEqual(value, env('FTP_HOST'))
        self.assertEqual(value, env('FTP').host)
        self.assertEqual('secret', env('FTP_PASSWORD'))
        self.assertEqual(None, env('FTP_USER'))
        self.assertEqual(None, env('SSL_COOKIE'))

    def test_getattr(self):
        a = Bunch({
            'hello': 'jinx',
        })
        values = a.__getattr__('values')
        self.assertEqual(values, { 'hello': 'jinx' })
