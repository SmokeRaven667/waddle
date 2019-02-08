from boto3.session import Session


__all__ = [
    'create_session',
    'ssm_client',
]


def create_session():
    """
    A handy helper function that will create the
    boto session using our waddle-level settings
    """
    import waddle
    session = Session(
        aws_access_key_id=waddle.aws_access_key_id,
        aws_secret_access_key=waddle.aws_secret_access_key,
        region_name=waddle.aws_region,
        profile_name=waddle.aws_profile,
    )
    return session


def ssm_client():
    session = create_session()
    return session.client('ssm')
