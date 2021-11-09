from os import environ


def load_from_env():
    if environ.get('SECRET_KEY') is None:
        raise ValueError('SECRET_KEY was not set. Please see the README for instructions on how to setup a .flaskenv file.')
    return {'SECRET_KEY': environ.get('SECRET_KEY')}
