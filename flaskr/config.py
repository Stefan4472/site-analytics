import pathlib
import dataclasses as dc
from os import environ
from dotenv import load_dotenv


@dc.dataclass
class SiteConfig:
    secret_key: str
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    database_name: str
    log_path: pathlib.Path = None
    sqlalchemy_track_modifications: bool = None

    @staticmethod
    def load_from_env(dotenv_path: str = None) -> 'SiteConfig':
        if dotenv_path:
            # Load environment variables
            load_dotenv(dotenv_path)
        return SiteConfig(
            environ.get('SECRET_KEY'),
            environ.get('POSTGRES_USERNAME'),
            environ.get('POSTGRES_PASSWORD'),
            environ.get('POSTGRES_HOST'),
            int(environ.get('POSTGRES_PORT')),
            environ.get('POSTGRES_DATABASE_NAME'),
            pathlib.Path(environ.get('SITEANALYTICS_LOG_PATH'))
                if environ.get('SITEANALYTICS_LOG_PATH') else None,
            bool(environ.get('SQLALCHEMY_TRACK_MODIFICATIONS'))
                if environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') else None,
        )
