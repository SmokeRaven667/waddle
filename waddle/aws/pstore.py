from typing import Generator, Tuple
from murmuration.aws import cached_client
from murmuration.helpers import prefix_alias
from .session import ssm_client


__all__ = [
    'yield_parameters',
    'put_parameter',
    'delete_parameters',
]


def yield_parameters(prefix) -> Generator[Tuple[str, str, str], None, None]:
    ssm = ssm_client()
    paginator = ssm.get_paginator('get_parameters_by_path')
    for page in paginator.paginate(
            Path=prefix,
            Recursive=True,
            WithDecryption=True,
            PaginationConfig={
                'PageSize': 10,
            }):
        for x in page['Parameters']:
            key = x['Name']
            value = x['Value']
            key = key.replace(prefix, '').replace('/', '.')[1:]
            yield key, value, x['Type']


def put_parameter(key, value, kms_key, encrypted):
    ssm = cached_client('ssm')
    params = {}
    if isinstance(value, list):
        value = ','.join([ f'{x}' for x in value ])
        params['Type'] = 'StringList'
    elif encrypted:
        params['Type'] = 'SecureString'
        if kms_key:
            params['KeyId'] = prefix_alias(kms_key)
    else:
        params['Type'] = 'String'
    result = ssm.put_parameter(Name=key, Value=value, Overwrite=True, **params)
    return result


def delete_parameters(*keys):
    ssm = cached_client('ssm')
    result = ssm.delete_parameters(Names=keys)
    return result
