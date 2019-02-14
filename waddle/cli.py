import pkg_resources
import click
from murmuration.aws import cached_client
from murmuration.helpers import prefix_alias
from murmuration.helpers import b64_str
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


if __name__ == "__main__":
    main()
