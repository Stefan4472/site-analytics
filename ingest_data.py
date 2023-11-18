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
from datetime import datetime
from pathlib import Path

import click
import requests

# The number of views to report in each call to the server.
# This must be within the requirements of the API.
BATCH_SIZE = 200


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
def ingest_data(
    traffic_csv: Path,
    host: str,
    port: int,
    password: str,
):
    """
    Reads records from the provided CSV file and sends `ReportTraffic` requests
    to the specified server.

    The CSV file should be comma-separated. It should not have a header. The
    expected format is `ISO_TIMESTAMP,URL,IP_ADDRESS,USER_AGENT`, with one
    record per line.

    TRAFFIC_CSV: path to the CSV file to ingest.
    HOST: address of the host site-analytics server, e.g. `127.0.0.1`.
    PORT: port of the host site-analytics server, e.g. `5000`.
    PASSWORD: secret key used to authenticate API requests, e.g. `dev-12345`.
    """
    click.echo(f"Will send requests to http://{host}:{port}.")
    start_time = datetime.now()
    with open(traffic_csv, newline="") as csvfile:
        reader = csv.DictReader(
            csvfile, fieldnames=["timestamp", "url", "ip_address", "user_agent"]
        )
        # Batch views into requests for improved performance.
        curr_batch = {"traffic": []}
        line = 1
        num_ingested = 0
        for row in reader:
            if len(row) != 4:
                raise ValueError(f"Invalid row at line {line}: {row}")
            curr_batch["traffic"].append(row)
            num_ingested += 1
            if len(curr_batch["traffic"]) == BATCH_SIZE:
                res = requests.post(
                    f"http://{host}:{port}/api/v1/traffic",
                    json=curr_batch,
                    headers={"Authorization": password},
                )
                if res.status_code != 200:
                    raise ValueError(
                        f"Request failed with status {res.status_code}: {res.text}"
                    )
                curr_batch["traffic"].clear()
    end_time = datetime.now()
    click.echo(
        f"Sent {num_ingested} records for ingestion. Took "
        f"{(end_time - start_time).seconds} seconds."
    )


if __name__ == "__main__":
    ingest_data()
