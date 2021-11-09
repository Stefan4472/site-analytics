from os import environ


def load_from_env():
    return {'SECRET_KEY': environ.get('SECRET_KEY')}
