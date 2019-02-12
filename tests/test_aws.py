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
        pass
        # session = create_session()
        # ssm = session.client('ssm')
        # ssm.put_parameter(
        #     Name='/test/waddle/cat', Value='cody', Type='String')
        # ssm.put_parameter(
        #     Name='/test/waddle/dog', Value='olive', Type='SecureString',
        #     Overwrite=True)

    # def test_session(self):
    #     session = create_session()
    #     self.assertEqual(session.profile_name, 'company')
    #     self.assertEqual(session.region_name, 'us-east-2')

    def test_yield_parameters(self):
        conf = ParamBunch()
        conf.load(prefix='/test')
        self.assertEqual(conf.waddle.cat, 'cody')
        self.assertEqual(conf.waddle.dog, 'olive')
        self.assertIn('waddle.cat', conf)

        conf = ParamBunch(prefix='test')
        self.assertEqual(conf.waddle.cat, 'cody')
        self.assertEqual(conf.waddle.dog, 'olive')
        self.assertIn('waddle.cat', conf)

    @staticmethod
    def delete_parameters():
        pass
        # session = create_session()
        # ssm = session.client('ssm')
        # ssm.delete_parameters(Names=[
        #     '/test/waddle/cat',
        #     '/test/waddle/dog',
        # ])

    def tearDown(self):
        Aws.delete_parameters()
        self.rehydrate_settings()
