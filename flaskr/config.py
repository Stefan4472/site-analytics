# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import dataclasses as dc
import pathlib
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
    def load_from_env(dotenv_path: str = None) -> "SiteConfig":
        if dotenv_path:
            # Load environment variables
            load_dotenv(dotenv_path)
        return SiteConfig(
            environ.get("SECRET_KEY"),
            environ.get("POSTGRES_USERNAME"),
            environ.get("POSTGRES_PASSWORD"),
            environ.get("POSTGRES_HOST"),
            int(environ.get("POSTGRES_PORT")),
            environ.get("POSTGRES_DATABASE_NAME"),
            pathlib.Path(environ.get("SITEANALYTICS_LOG_PATH"))
            if environ.get("SITEANALYTICS_LOG_PATH")
            else None,
            bool(environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"))
            if environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
            else None,
        )
