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
import csv
from pathlib import Path
from typing import Optional

import click
import requests


@click.command()
@click.argument(
    "traffic_csv",
    type=click.Path(
        file_okay=True, dir_okay=False, exists=True, readable=True, path_type=Path
    ),
)
@click.argument("host", type=str)
@click.argument("port", type=int)
@click.password_option(required=True)
@click.option("--max_records", type=int, help="Limits the number of records to ingest.")
def ingest_data(
    traffic_csv: Path,
    host: str,
    port: int,
    password: str,
    max_records: Optional[int] = None,
):
    """
    Reads records from the provided CSV file and sends `ReportTraffic` requests
    to the specified server.

    The CSV file should be comma-separated. It should not have a header. The
    expected format is `URL,IP_ADDRESS,USER_AGENT,ISO_TIMESTAMP`, with one
    record per line.

    TRAFFIC_CSV: path to the CSV file to ingest.
    HOST: address of the host site-analytics server, e.g. `127.0.0.1`.
    PORT: port of the host site-analytics server, e.g. `5000`.
    PASSWORD: secret key used to authenticate API requests, e.g. `dev-12345`.
    """
    click.echo(f"Will send requests to http://{host}:{port}.")
    with open(traffic_csv, newline="") as csvfile:
        reader = csv.reader(csvfile)
        line = 1
        for row in reader:
            if max_records is not None and line > max_records:
                break
            if len(row) != 4:
                raise ValueError(f"Invalid row at line {line}: {row}")
            # TODO: batching?
            res = requests.post(
                f"http://{host}:{port}/api/v1/traffic",
                json={
                    "url": row[0],
                    "ip_address": row[1],
                    "user_agent": row[2],
                    "timestamp": row[3],
                },
                headers={"Authorization": password},
            )
            if res.status_code != 200:
                raise ValueError(
                    f"Request failed with status {res.status_code}: {res.text}"
                )
            line += 1
        click.echo(f"Sent {line-1} records for ingestion.")


if __name__ == "__main__":
    ingest_data()
