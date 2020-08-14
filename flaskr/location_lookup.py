import requests
import json
import typing
import dataclasses as dc


# Used for accessing the `freegeoip` API
LOCATION_API_URL = "https://freegeoip.app/json/"
LOCATION_API_HEADERS = {
    'accept': "application/json",
    'content-type': "application/json"
}


@dc.dataclass
class Location:
    country_name: str = 'UNKNOWN'
    city: str = 'UNKNOWN'
    region_name: str = 'UNKNOWN'


def location_from_ip(
        ip_addr: str,
) -> Location:
    request_url = LOCATION_API_URL + ip_addr
    try:
        response_str = requests.request(
            "GET",
            request_url,
            headers=LOCATION_API_HEADERS,
        ).text
        
        if response_str.strip() == '404 page not found':
            return Location()
        else:
            response_json = json.loads(response_str)
            print(response_json)
            # Build kwargs for `Location` instance
            location_kwargs = {}
            if response_json.get('country_name'):
                location_kwargs['country_name'] = response_json['country_name']
            if response_json.get('city'):
                location_kwargs['city'] = response_json['city']
            if response_json.get('region_name'):
                location_kwargs['region_name'] = response_json['region_name']
            return Location(**location_kwargs)
    except json.decoder.JSONDecodeError as e:
        return Location
  

# def country_from_ip(ip_addr: str):
#   location_data = location_from_ip(ip_addr)
#   if location_data and 'country_code' in location_data:
#     return location_data['country_code']
#   else:
#     return ''


# def city_from_ip(ip_addr):
#   location_data = location_from_ip(ip_addr)
#   if location_data and 'city' in location_data:
#     return location_data['city']
#   else:
#     return ''


# def region_from_ip(ip_addr):
#   location_data = location_from_ip(ip_addr)
#   if location_data and 'region_code' in location_data:
#     return location_data['region_code']
#   else:
#     return ''