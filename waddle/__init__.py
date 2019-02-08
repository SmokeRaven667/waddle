"""
Contains a number of useful modules for handling
configuration and encryption using aws parameter store
and kms
"""
from .bunch import *  # noqa
from .param_bunch import *  # noqa


# settings to control aws connection
aws_profile = None
aws_secret_access_key = None
aws_access_key_id = None
aws_region = None
