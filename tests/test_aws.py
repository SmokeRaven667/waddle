import os
from unittest import TestCase
from waddle import settings
from waddle.aws import create_session
from waddle import ParamBunch


__all__ = [
    'Aws',
]


class Aws(TestCase):
    settings_keys = [
        'aws_region',
        'aws_profile',
        'aws_access_key_id',
        'aws_secret_access_key',
    ]

    def save_settings(self):
        self.settings = {}
        for key in self.settings_keys:
            value = getattr(settings, key, None)
            self.settings[key] = value

    def rehydrate_settings(self):
        for key, value in self.settings.items():
            setattr(settings, key, value)

    def setUp(self):
        self.save_settings()
        keys = [ 'AWS_REGION', 'AWS_PROFILE', 'AWS_ACCESS_KEY_ID',
                 'AWS_SECRET_ACCESS_KEY' ]
        for key in keys:
            setattr(settings, key.lower(), os.environ.get(key))
        Aws.setup_parameters()

    @staticmethod
    def setup_parameters():
        session = create_session()
        ssm = session.client('ssm')
        ssm.put_parameter(
            Name='/test/waddle/cat', Value='cody', Type='String',
            Overwrite=True)
        ssm.put_parameter(
            Name='/test/waddle/dog', Value='olive', Type='SecureString',
            Overwrite=True)

    def test_yield_parameters(self):
        conf = ParamBunch()
        conf.load(prefix='/test')
        self.assertEqual(conf.waddle.cat, 'cody')
        self.assertEqual(conf.waddle.dog, 'olive')
        self.assertIn('waddle.cat', conf)
        self.assertIn('waddle.dog', conf.encrypted)
        conf.waddle.dog = 'peanut'
        conf.waddle.secret = 'test of secrets'
        conf.encrypted.append('waddle.secret')
        conf.to_aws()

        conf.load(prefix='/test')
        self.assertIn('waddle.dog', conf.encrypted)
        self.assertIn('waddle.secret', conf.encrypted)
        self.assertEqual(conf.waddle.dog, 'peanut')
        self.assertEqual(conf.waddle.secret, 'test of secrets')
        self.assertEqual(conf.waddle.cat, 'cody')

        conf.waddle.cat = [ 'cody', 'jinx' ]
        conf.meta.kms_key = 'dev'
        conf.to_aws()
        conf = ParamBunch(prefix='test')
        self.assertEqual(conf.waddle.dog, 'peanut')
        self.assertEqual(conf.waddle.secret, 'test of secrets')
        self.assertIn('jinx', conf.waddle.cat)

    @staticmethod
    def delete_parameters():
        session = create_session()
        ssm = session.client('ssm')
        ssm.delete_parameters(Names=[
            '/test/waddle/cat',
            '/test/waddle/dog',
            '/test/waddle/secret',
        ])

    def tearDown(self):
        Aws.delete_parameters()
        self.rehydrate_settings()
