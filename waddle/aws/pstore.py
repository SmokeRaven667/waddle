from typing import Generator, Tuple
from .session import ssm_client


__all__ = [
    'yield_parameters',
]


def yield_parameters(prefix) -> Generator[Tuple[str, str], None, None]:
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
            print(f'yielding {key}, {value}')
            yield key, value


# def push_parameters(prefix):
#     pass
