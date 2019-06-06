import os
from shutil import copyfile
from unittest import TestCase
from click.testing import CliRunner
from waddle import cli
from waddle.param_bunch import ParamBunch
from waddle.aws import yield_parameters


class TestCli(TestCase):
    def test_cli(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--version'])
        self.assertIn('waddle', result.output)

    def test_add_key(self):
        filename = 'tests/conf/secret.yml'
        copyfile('tests/conf/nested.yml', filename)
        self.add_secret(filename)
        self.add_secret_failure()
        os.remove(filename)

    def test_comment_preservation(self):
        filename = 'tests/conf/add_key.yml'
        copyfile('tests/conf/add_key.input.yml', filename)
        b = ParamBunch()
        b.load(filename=filename)
        b.waddle.preferred = 'cats'
        b.save(filename=filename)
        with open(filename, 'r') as f:
            data = f.read()
        self.assertIn('# these are the development dogs', data)
        self.assertIn('# these are the development cats', data)
        os.remove(filename)

    def add_secret(self, filename):
        secret = 'this is super secret'
        runner = CliRunner()
        runner.invoke(
            cli.main, [
                'add-secret',
                '-f',
                filename,
                'waddle.secret',
            ], input=f'{secret}\n')

        b = ParamBunch()
        b.load(filename=filename)
        self.assertIn('cody', b.waddle.cats)
        self.assertEqual(b.waddle.preferred, 'cats')
        self.assertEqual(b.waddle.secret, secret)
        self.assertIn('waddle.secret', b.encrypted)

    def add_secret_failure(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.main, [
                'add-secret',
                '-f',
                'tests/conf/encrypted.yml',
                'waddle.secret',
            ], input=f'whatwhat\n')
        self.assertIn('does not have a kms key specified', result.output)

    def test_is_secret(self):
        self.assertTrue(cli.is_secret('some.secret'))
        self.assertTrue(cli.is_secret('some.password'))
        self.assertFalse(cli.is_secret('some.username'))
        self.assertTrue(cli.is_secret('some.api_key'))
        self.assertTrue(cli.is_secret('some.oauth_token'))

    def test_encrypt(self):
        filename = 'tests/conf/test.yml'
        copyfile('tests/conf/cli-encrypt.yml', filename)
        runner = CliRunner()
        runner.invoke(
            cli.main, [
                'encrypt',
                '-f',
                filename,
            ])
        x = ParamBunch()
        x.load(filename=filename, decrypt=False)
        self.assertNotEqual(x.waddle.db.password, 'cody')
        self.assertNotEqual(x.waddle.api.token, 'taylor')
        self.assertEqual(x.waddle.public, 'jinx')
        self.assertNotEqual(x.oauth.token, 'padme')
        self.assertNotEqual(x.waddle.secret.favorite_dog, 'peanut')
        os.remove(filename)

    def test_encrypt_failure(self):
        runner = CliRunner()
        result = runner.invoke(
            cli.main, [
                'encrypt',
                '-f',
                'tests/conf/encrypted.yml',
            ], input=f'whatwhat\n')
        self.assertIn('does not have a kms key specified', result.output)

    def test_deploy(self):
        runner = CliRunner()
        filename = 'tests/conf/deploy.yml'
        runner.invoke(
            cli.main,
            [ 'deploy', '-f', filename, ])
        conf = ParamBunch(prefix='/test')
        self.assertEqual(conf.waddle.cat, 'stella')
        self.assertEqual(conf.waddle.dog, 'olive')
        runner.invoke(
            cli.main,
            [ 'undeploy', '-f', filename, ])
        deleted_keys = [ '/test/waddle/cat', '/test/waddle/dog', ]
        for key in yield_parameters('/test'):
            self.assertNotIn(key, deleted_keys)
