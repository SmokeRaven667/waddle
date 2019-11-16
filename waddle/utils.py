import os


__all__ = [
    'load_config',
]


def load_config(*filenames):
    """
    Loads the specified config files if they exist in the order
    specified.  This is useful for having "cascading" configs
    and also for suppressing warnings from `ParamBunch.from_file`
    """
    from .param_bunch import ParamBunch
    conf = ParamBunch()
    for x in filenames:
        if os.path.exists(x):
            conf.from_file(x)
    return conf
