import os
from subprocess import Popen
from unittest import TestCase
import waddle
from waddle.aws import create_session
from waddle.aws import yield_parameters
from waddle import Bunch


__all__ = [
    'Aws',
]


class Aws(TestCase):
    def setUp(self):
        region = os.environ.get('AWS_REGION', 'us-east-2')
        access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', 'cody')
        secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', 'jinx')
        handle = Popen([
            '/bin/bash',
            '-c',
            f'source bin/activate '
            f'  && aws --profile=company configure set region {region}'
            f'  && aws --profile=company configure '
            f'set aws_access_key_id {access_key_id}'
            f'  && aws --profile=company configure set '
            f'aws_secret_access_key {secret_access_key}' ])
        handle.communicate()
        self.setup_parameters()

    def setup_parameters(self):
        self.aws_profile = waddle.aws_profile
        self.aws_region = waddle.aws_region
        waddle.aws_profile = 'company'
        waddle.aws_region = 'us-east-2'
        waddle.aws_profile = 'company'
        session = create_session()
        ssm = session.client('ssm')
        ssm.put_parameter(
            Name='/test/waddle/cat', Value='cody', Type='String')
        ssm.put_parameter(
            Name='/test/waddle/dog', Value='olive', Type='SecureString',
            Overwrite=True)

    # def test_session(self):
    #     session = create_session()
    #     self.assertEqual(session.profile_name, 'company')
    #     self.assertEqual(session.region_name, 'us-east-2')

    def test_yield_parameters(self):
        conf = Bunch()
        for key, value in yield_parameters('/test'):
            conf[key] = value
        self.assertEqual(conf.waddle.cat, 'cody')
        self.assertEqual(conf.waddle.dog, 'olive')
        self.assertIn('waddle.cat', conf)

    def delete_parameters(self):
        session = create_session()
        ssm = session.client('ssm')
        ssm.delete_parameters(Names=[
            '/test/waddle/cat',
            '/test/waddle/dog',
        ])
        waddle.aws_profile = self.aws_profile
        waddle.aws_region = self.aws_region

    def tearDown(self):
        self.delete_parameters()
