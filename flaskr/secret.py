import pathlib

# Secret key used by default
DEFAULT_SECRET_KEY = 'dev'


def load_secret_key(
        secret_path: pathlib.Path,
) -> str:
    with open(secret_path, 'r') as f:
        return f.read().strip()
