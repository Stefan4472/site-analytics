import requests
import dataclasses as dc


@dc.dataclass
class Location:
    country_name: str = None
    city: str = None
    region_name: str = None


# Used for accessing the `freegeoip` API
LOCATION_API_URL = "https://freegeoip.app/json/"
LOCATION_API_HEADERS = {
    'accept': "application/json",
    'content-type': "application/json"
}


def request_location_info(ip_addr: str) -> Location:
    """Query the FreeGeoIP API."""
    response = requests.request(
        'GET',
        LOCATION_API_URL + ip_addr,
        headers=LOCATION_API_HEADERS,
    )
    if response.status_code == 200:
        return Location(
            country_name=response.json().get('country_name'),
            city=response.json().get('city'),
            region_name=response.json().get('region_name'),
        )
    else:
        raise ValueError(response.text)
