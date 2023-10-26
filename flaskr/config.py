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
from dataclasses import dataclass
from os import environ

from dotenv import load_dotenv


@dataclass
class SiteConfig:
    secret_key: str
    instance_path: str

    @staticmethod
    def load_from_env() -> "SiteConfig":
        """Instantiates config values from environment variables."""
        # Attempt to load a `.flaskenv` configuration file.
        load_dotenv(".flaskenv")
        return SiteConfig(
            environ.get("SITE_ANALYTICS_SECRET_KEY"),
            environ.get("SITE_ANALYTICS_INSTANCE_PATH"),
        )


def validate_config(cfg: SiteConfig):
    """Validates that the provided configuration is proper."""
    if not cfg.secret_key:
        raise ValueError(f"No secret key has been configured.")
    if not cfg.instance_path:
        raise ValueError(f"No instance path has been configured.")
