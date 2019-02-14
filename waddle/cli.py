import sys
import click
import pkg_resources
from murmuration.aws import cached_client
from murmuration.helpers import prefix_alias
from murmuration.helpers import b64_str
from murmuration import gcm
from murmuration import kms
from murmuration.helpers import from_b64_str
from .param_bunch import ParamBunch


def version():
    data_file = pkg_resources.resource_filename('waddle', 'version')
    with open(data_file, 'r') as f:
        x = f.read()
        x = x.strip()
        return x


@click.group(name='waddle')
@click.version_option(version())
def main():
    "cli for managing waddle config files"


@main.command(name='add-key')
@click.argument('kms_key', metavar='key_alias', )
@click.argument('filename', metavar='/path/to/config_file.yml',
                type=click.Path(exists=True))
@click.option('-r', '--region', metavar='region')
@click.option('-p', '--profile', metavar='profile name')
def add_key(kms_key, filename, region=None, profile=None):
    """
    Adds a key encrypted by the specified kms key
    and adds it to the specified configuration file

    Example:
        waddle add-key -p profile -r us-east-2 dev ./conf/dev.yml
    """
    x = ParamBunch()
    x.load(filename=filename)
    if x.meta.encryption_key:
        print(f'{filename} already has an encryption key.  '
              f'Use rekey to change encryption keys')
        return
    client = cached_client('kms', region=region, profile=profile)
    key_alias = prefix_alias(kms_key)
    response = client.generate_data_key(KeyId=key_alias, KeySpec='AES_256')
    key = response['CiphertextBlob']
    key = b64_str(key)
    x.meta.kms_key = kms_key
    x.meta.encryption_key = key
    x.save(filename=filename)


@main.command(name='add-secret')
@click.argument('key', metavar='db.password')
@click.option('-f', '--filename', metavar='/path/to/config_file.yml',
              type=click.Path(exists=True), required=True)
@click.option('-r', '--region', metavar='region')
@click.option('-p', '--profile', metavar='profile name')
def add_secret(filename, key, region, profile):
    """
    Adds an encrypted secret to the specified configuration file

    Example:
        waddle add-secret -f conf/dev.yml db.password
    """
    x = ParamBunch()
    x.load(filename=filename, decrypt=False)
    if not x.meta.encryption_key:
        print(f'{filename} does not have an encryption key.  '
              f'Use add-key to add one.')
        return
    tty = sys.stdin.isatty()
    if tty:
        print(f'Enter value for [{key}]: ', end='', file=sys.stderr)
        sys.stderr.flush()
    # stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)
    plain_text = sys.stdin.readline().rstrip()
    # plain_text = plain_text.decode('utf-8').rstrip()
    encryption_key = from_b64_str(x.meta.encryption_key)
    encryption_key = kms.decrypt_bytes(encryption_key, region, profile)
    x[key] = gcm.encrypt(plain_text, encryption_key, x.meta.encryption_key)
    x.save(filename)


if __name__ == "__main__":
    main()
