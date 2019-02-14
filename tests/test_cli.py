import os
from shutil import copyfile
from unittest import TestCase
from click.testing import CliRunner
from waddle import cli
from waddle.param_bunch import ParamBunch


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
