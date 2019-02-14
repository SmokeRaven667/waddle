import sys
import click
import pkg_resources
from murmuration import kms_wrapped
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


@main.command(name='add-secret')
@click.argument('key', metavar='db.password')
@click.option('-f', '--filename', metavar='/path/to/config_file.yml',
              type=click.Path(exists=True), required=True)
def add_secret(filename, key):
    """
    Adds an encrypted secret to the specified configuration file

    Example:
        waddle add-secret -f conf/dev.yml db.password
    """
    x = ParamBunch()
    x.load(filename=filename, decrypt=False)
    kms_key = x.get('meta.kms_key')
    if not kms_key:
        print(f'{filename} does not have a kms key specified.')
        return
    tty = sys.stdin.isatty()
    if tty:
        print(f'Enter value for [{key}]: ', end='', file=sys.stderr)
        sys.stderr.flush()
    # stdin = os.fdopen(sys.stdin.fileno(), 'rb', 0)
    plain_text = sys.stdin.readline().rstrip()
    # plain_text = plain_text.decode('utf-8').rstrip()
    region = x.get('meta.region')
    profile = x.get('meta.profile')
    x[key] = kms_wrapped.encrypt(plain_text, kms_key, region, profile)
    x.save(filename)


if __name__ == "__main__":
    main()
