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
import sys
from datetime import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt
import pygal
import requests

"""Quick script to make API requests and create plots."""


def make_request(params: dict, auth_key: str) -> List:
    r = requests.get(
        "http://127.0.0.1:5000/api/v1/data/statistics",
        headers={"Authorization": auth_key},
        params=params,
    )
    if r.status_code == 401:
        raise ValueError("Authentication failed")
    return r.json()


def format_date(date: datetime):
    return datetime.strftime(date, "%m-%d-%Y")


def parse_timeboxed_data(_json) -> ([datetime], [str], [int]):
    dates: List[datetime] = []
    keys: List[str] = []
    counts: List[int] = []
    for row in _json:
        # Format: "Mon, 05 Oct 2020 00:00:00 GMT"
        dates.append(datetime.strptime(row["date"], "%a, %d %b %Y %H:%M:%S %Z"))
        keys.append(row["key"])
        counts.append(row["quantity"])
    return dates, keys, counts


def plot_views_per_week(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    base_params = {
        "count_what": "Views",
        "group_what": "Nothing",
        "resolution": "Week",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    bot_params = dict(base_params, query_on="Bots")
    bot_views_per_week = make_request(bot_params, auth_key)
    bdates, bkeys, bcounts = parse_timeboxed_data(bot_views_per_week)

    people_params = dict(base_params, query_on="People")
    people_views_per_week = make_request(people_params, auth_key)
    pdates, pkeys, pcounts = parse_timeboxed_data(people_views_per_week)

    fig, ax = plt.subplots()
    fig.suptitle("Views per Week")
    ax.set_ylabel("Number of Views")
    ax.plot(bdates, bcounts, label="Bots", linestyle="--")
    ax.plot(pdates, pcounts, label="People", linestyle="--")
    ax.grid(True)
    fig.legend()
    # Rotate tick labels 45 degrees https://stackoverflow.com/a/56139690
    plt.draw()
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    fig.subplots_adjust(bottom=0.15)
    return fig, ax


def plot_all_time_bot_urls(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    params = {
        "query_on": "Bots",
        "count_what": "Views",
        "group_what": "Url",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    urls_all_time = make_request(params, auth_key)
    top_ten = sorted(urls_all_time, key=lambda x: x["quantity"], reverse=True)[:10]
    keys = [b["key"] for b in top_ten]
    vals = [b["quantity"] for b in top_ten]
    fig, ax = plt.subplots()
    fig.suptitle("Most Visited URLs (Bots)")
    ax.set_xlabel("Number of views")
    ax.set_ylabel("Url")
    ax.barh(keys, vals)
    ax.get_yaxis().set_ticks([])
    # https://stackoverflow.com/a/30229062
    for i, v in enumerate(vals):
        ax.text(v + 20, i - 0.15, keys[i], color="black", fontweight="bold")
    return fig, ax


def plot_all_time_person_urls(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    params = {
        "query_on": "People",
        "count_what": "Views",
        "group_what": "Url",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    urls_all_time = make_request(params, auth_key)
    top_ten = sorted(urls_all_time, key=lambda x: x["quantity"], reverse=True)[:10]
    keys = [b["key"] for b in top_ten]
    vals = [b["quantity"] for b in top_ten]
    fig, ax = plt.subplots()
    fig.suptitle("Most Visited URLs (People)")
    ax.set_xlabel("Number of views")
    ax.set_ylabel("Url")
    ax.barh(keys, vals)
    ax.get_yaxis().set_ticks([])
    # https://stackoverflow.com/a/30229062
    for i, v in enumerate(vals):
        ax.text(v + 20, i - 0.15, keys[i], color="black", fontweight="bold")
    return fig, ax


def plot_all_time_bot_domains(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    """Bot domains by number of views, all time."""
    params = {
        "query_on": "Bots",
        "count_what": "Views",
        "group_what": "Domain",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    bot_domains_all_time = make_request(params, auth_key)
    bot_domains_all_time = [b for b in bot_domains_all_time if b["key"] is not None]
    top_ten = sorted(bot_domains_all_time, key=lambda x: x["quantity"], reverse=True)[
        :10
    ]
    keys = [b["key"] for b in top_ten]
    vals = [b["quantity"] for b in top_ten]
    fig, ax = plt.subplots()
    fig.suptitle("Top Ten Bot Domains")
    ax.set_xlabel("Number of views")
    ax.barh(keys, vals)
    fig.subplots_adjust(left=0.22)
    for i, v in enumerate(vals):
        ax.text(v, i - 0.15, vals[i], color="black", fontweight="bold")
    return fig, ax


def sort_pie_data(data: dict) -> Tuple[List, List]:
    as_tuples = [(k, v) for k, v in data.items()]
    as_tuples.sort(key=lambda x: x[1], reverse=True)
    labels = [t[0] for t in as_tuples]
    vals = [t[1] for t in as_tuples]
    return labels, vals


def plot_all_time_person_os(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    """Operating Systems by number of person-users, all time."""
    params = {
        "query_on": "People",
        "count_what": "Users",
        "group_what": "OperatingSystem",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    people_os_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_os_all_time = {
        "Android": 0,
        "iOS": 0,
        "Linux/Unix": 0,
        "MAC": 0,
        "Windows": 0,
        "Other": 0,
    }
    for data in people_os_all_time:
        if data["key"].startswith("Android"):
            binned_os_all_time["Android"] += data["quantity"]
        elif data["key"].startswith("iOS"):
            binned_os_all_time["iOS"] += data["quantity"]
        elif data["key"].startswith("Linux") or data["key"].startswith("Ubuntu"):
            binned_os_all_time["Linux/Unix"] += data["quantity"]
        elif data["key"].startswith("Mac"):
            binned_os_all_time["MAC"] += data["quantity"]
        elif data["key"].startswith("Windows"):
            binned_os_all_time["Windows"] += data["quantity"]
        else:
            binned_os_all_time["Other"] += data["quantity"]

    fig, ax = plt.subplots()
    fig.suptitle("Person Operating Systems")
    ax.pie(
        binned_os_all_time.values(), labels=binned_os_all_time.keys(), autopct="%1.0f%%"
    )
    fig.tight_layout()
    return fig, ax


def plot_all_time_person_devices(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    """Devices by number of person-users, all time."""
    params = {
        "query_on": "People",
        "count_what": "Users",
        "group_what": "Device",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    people_devices_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_devices_all_time = {
        "Huawei": 0,
        "Apple": 0,
        "XiaoMi": 0,
        "Samsung": 0,
        "Google": 0,
        "Other Android": 0,
        "Other": 0,
        "Unknown": 0,
    }
    for data in people_devices_all_time:
        if "Huawei" in data["key"]:
            binned_devices_all_time["Huawei"] += data["quantity"]
        elif "Apple" in data["key"]:
            binned_devices_all_time["Apple"] += data["quantity"]
        elif "XiaoMi" in data["key"]:
            binned_devices_all_time["XiaoMi"] += data["quantity"]
        elif "Samsung" in data["key"]:
            binned_devices_all_time["Samsung"] += data["quantity"]
        elif "Android" in data["key"]:
            binned_devices_all_time["Other Android"] += data["quantity"]
        elif "Google" in data["key"]:
            binned_devices_all_time["Google"] += data["quantity"]
        elif data["key"] == "" or "Generic" in data["key"]:
            binned_devices_all_time["Unknown"] += data["quantity"]
        else:
            binned_devices_all_time["Other"] += data["quantity"]

    fig, ax = plt.subplots()
    fig.suptitle("Device Manufacturers (People Users)")
    labels, vals = sort_pie_data(binned_devices_all_time)
    ax.pie(vals, autopct=lambda pct: ("%1.0f%%" % pct) if pct > 2 else "")
    ax.legend(labels)
    fig.tight_layout()
    return fig, ax


def plot_all_time_device_types(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    """Devices by number of person-users, all time."""
    params = {
        "query_on": "People",
        "count_what": "Users",
        "group_what": "DeviceType",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    people_devices_all_time = make_request(params, auth_key)
    values = [d["quantity"] for d in people_devices_all_time]
    labels = [d["key"] for d in people_devices_all_time]
    labels[labels.index("")] = "Unknown"
    fig, ax = plt.subplots()
    fig.suptitle("Device Types")
    ax.pie(values, labels=labels, autopct="%1.0f%%")
    return fig, ax


def plot_all_time_person_browsers(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> Tuple["plt.Figure", "plt.Axes"]:
    """Browser by number of person-users, all time."""
    params = {
        "query_on": "People",
        "count_what": "Users",
        "group_what": "Browser",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    people_browsers_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_browsers_all_time = {
        "Chrome": 0,
        "Edge": 0,
        "Firefox": 0,
        "Safari": 0,
        "Opera": 0,
        "IE": 0,
        "Http-Client": 0,
        "Other": 0,
        "Unknown": 0,
    }
    for data in people_browsers_all_time:
        if "Chrome" in data["key"]:
            binned_browsers_all_time["Chrome"] += data["quantity"]
        elif "Edge" in data["key"]:
            binned_browsers_all_time["Edge"] += data["quantity"]
        elif "Firefox" in data["key"]:
            binned_browsers_all_time["Firefox"] += data["quantity"]
        elif "Safari" in data["key"]:
            binned_browsers_all_time["Safari"] += data["quantity"]
        elif "Opera" in data["key"]:
            binned_browsers_all_time["Opera"] += data["quantity"]
        elif "IE" in data["key"]:
            binned_browsers_all_time["IE"] += data["quantity"]
        elif "Other" in data["key"]:
            binned_browsers_all_time["Unknown"] += data["quantity"]
        elif "Http" in data["key"] or "http" in data["key"]:
            binned_browsers_all_time["Http-Client"] += data["quantity"]
        else:
            binned_browsers_all_time["Other"] += data["quantity"]
    as_tuples = [(k, v) for k, v in binned_browsers_all_time.items()]
    as_tuples.sort(key=lambda x: x[1], reverse=True)
    labels = [t[0] for t in as_tuples]
    vals = [t[1] for t in as_tuples]
    fig, ax = plt.subplots()
    fig.suptitle("Person Browsers")
    ax.pie(
        vals, labels=labels, autopct=lambda pct: ("%1.0f%%" % pct) if pct > 3 else ""
    )
    return fig, ax


# Map Geo-API country name to pygal country code
COUNTRY_CODE_MAPPING = {
    "Andorra": "ad",
    "United Arab Emirates": "ae",
    "Afghanistan": "af",
    "Albania": "al",
    "Armenia": "am",
    "Angola": "ao",
    "Antarctica": "aq",
    "Argentina": "ar",
    "Austria": "at",
    "Australia": "au",
    "Azerbaijan": "az",
    "Bosnia and Herzegovina": "ba",
    "Bangladesh": "bd",
    "Belgium": "be",
    "Burkina Faso": "bf",
    "Bulgaria": "bg",
    "Bahrain": "bh",
    "Burundi": "bi",
    "Benin": "bj",
    "Brunei Darussalam": "bn",
    "Bolivia, Plurinational State of": "bo",
    "Brazil": "br",
    "Bhutan": "bt",
    "Botswana": "bw",
    "Belarus": "by",
    "Belize": "bz",
    "Canada": "ca",
    "Congo, the Democratic Republic of the": "cd",
    "Central African Republic": "cf",
    "Congo": "cg",
    "Switzerland": "ch",
    "Ivory Coast": "ci",
    "Chile": "cl",
    "Cameroon": "cm",
    "China": "cn",
    "Colombia": "co",
    "Costa Rica": "cr",
    "Cuba": "cu",
    "Cape Verde": "cv",
    "Cyprus": "cy",
    "Czechia": "cz",
    "Germany": "de",
    "Djibouti": "dj",
    "Denmark": "dk",
    "Dominican Republic": "do",
    "Algeria": "dz",
    "Ecuador": "ec",
    "Estonia": "ee",
    "Egypt": "eg",
    "Western Sahara": "eh",
    "Eritrea": "er",
    "Spain": "es",
    "Ethiopia": "et",
    "Finland": "fi",
    "France": "fr",
    "Gabon": "ga",
    "United Kingdom": "gb",
    "Georgia": "ge",
    "French Guiana": "gf",
    "Ghana": "gh",
    "Greenland": "gl",
    "Gambia": "gm",
    "Guinea": "gn",
    "Equatorial Guinea": "gq",
    "Greece": "gr",
    "Guatemala": "gt",
    "Guam": "gu",
    "Guinea-Bissau": "gw",
    "Guyana": "gy",
    "Hong Kong": "hk",
    "Honduras": "hn",
    "Croatia": "hr",
    "Haiti": "ht",
    "Hungary": "hu",
    "Indonesia": "id",
    "Ireland": "ie",
    "Israel": "il",
    "India": "in",
    "Iraq": "iq",
    "Iran, Islamic Republic of": "ir",
    "Iceland": "is",
    "Italy": "it",
    "Jamaica": "jm",
    "Jordan": "jo",
    "Japan": "jp",
    "Kenya": "ke",
    "Kyrgyzstan": "kg",
    "Cambodia": "kh",
    "Korea Korea": "kp",
    "South Korea": "kr",
    "Kuwait": "kw",
    "Kazakhstan": "kz",
    "Lao People’s Democratic Republic": "la",
    "Lebanon": "lb",
    "Liechtenstein": "li",
    "Sri Lanka": "lk",
    "Liberia": "lr",
    "Lesotho": "ls",
    "Lithuania": "lt",
    "Luxembourg": "lu",
    "Latvia": "lv",
    "Libyan Arab Jamahiriya": "ly",
    "Morocco": "ma",
    "Monaco": "mc",
    "Moldova, Republic of": "md",
    "Montenegro": "me",
    "Madagascar": "mg",
    "North Macedonia": "mk",
    "Mali": "ml",
    "Myanmar": "mm",
    "Mongolia": "mn",
    "Macao": "mo",
    "Mauritania": "mr",
    "Malta": "mt",
    "Mauritius": "mu",
    "Maldives": "mv",
    "Malawi": "mw",
    "Mexico": "mx",
    "Malaysia": "my",
    "Mozambique": "mz",
    "Namibia": "na",
    "Niger": "ne",
    "Nigeria": "ng",
    "Nicaragua": "ni",
    "Netherlands": "nl",
    "Norway": "no",
    "Nepal": "np",
    "New Zealand": "nz",
    "Oman": "om",
    "Panama": "pa",
    "Peru": "pe",
    "Papua New Guinea": "pg",
    "Philippines": "ph",
    "Pakistan": "pk",
    "Poland": "pl",
    "Puerto Rico": "pr",
    "Palestine, State of": "ps",
    "Portugal": "pt",
    "Paraguay": "py",
    "Reunion": "re",
    "Romania": "ro",
    "Serbia": "rs",
    "Russia": "ru",
    "Rwanda": "rw",
    "Saudi Arabia": "sa",
    "Seychelles": "sc",
    "Sudan": "sd",
    "Sweden": "se",
    "Singapore": "sg",
    "Saint Helena, Ascension and Tristan da Cunha": "sh",
    "Slovenia": "si",
    "Slovakia": "sk",
    "Sierra Leone": "sl",
    "San Marino": "sm",
    "Senegal": "sn",
    "Somalia": "so",
    "Suriname": "sr",
    "Sao Tome and Principe": "st",
    "El Salvador": "sv",
    "Syrian Arab Republic": "sy",
    "Swaziland": "sz",
    "Chad": "td",
    "Togo": "tg",
    "Thailand": "th",
    "Tajikistan": "tj",
    "Timor-Leste": "tl",
    "Turkmenistan": "tm",
    "Tunisia": "tn",
    "Turkey": "tr",
    "Taiwan (Republic of China)": "tw",
    "Tanzania, United Republic of": "tz",
    "Ukraine": "ua",
    "Uganda": "ug",
    "United States": "us",
    "Uruguay": "uy",
    "Uzbekistan": "uz",
    "Holy See (Vatican City State)": "va",
    "Venezuela": "ve",
    "Vietnam": "vn",
    "Yemen": "ye",
    "Mayotte": "yt",
    "South Africa": "za",
    "Zambia": "zm",
    "Zimbabwe": "zw",
}


def plot_bot_views_per_country(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> "pygal.maps.world.World":
    """Return pygal world map with number of bot-views per country."""
    params = {
        "query_on": "Bots",
        "count_what": "Views",
        "group_what": "Country",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    views_by_country = make_request(params, auth_key)
    # Filter out the '' country name (i.e., unknown)
    views_by_country = [v for v in views_by_country if v["key"] != ""]
    # Convert country names to pygal country codes
    country_data = {
        COUNTRY_CODE_MAPPING[v["key"]]: v["quantity"] for v in views_by_country
    }
    map = pygal.maps.world.World(style=pygal.style.RedBlueStyle)
    map.title = "Views by Country (Bots)"
    map.add("", country_data)
    return map


def plot_person_views_per_country(
    start_date: datetime,
    end_date: datetime,
    auth_key: str,
) -> "pygal.maps.world.World":
    """Return pygal world map with number of person-users per country."""
    params = {
        "query_on": "People",
        "count_what": "Users",
        "group_what": "Country",
        "resolution": "All",
        "start_date": format_date(start_date),
        "end_date": format_date(end_date),
    }
    views_by_country = make_request(params, auth_key)
    # Filter out the '' country name and 'Guernsey'
    views_by_country = [
        v for v in views_by_country if v["key"] != "" and v["key"] != "Guernsey"
    ]
    # Convert country names to pygal country codes
    country_data = {
        COUNTRY_CODE_MAPPING[v["key"]]: v["quantity"] for v in views_by_country
    }
    from pygal.style import BlueStyle

    map = pygal.maps.world.World(style=BlueStyle)
    map.title = "Unique IP Addresses by Country (People)"
    map.add("", country_data)
    return map


if __name__ == "__main__":
    """Usage: make_plots.py [AUTH_KEY]"""
    if len(sys.argv) != 2:
        raise ValueError("Invalid number of arguments, pass AUTH_KEY as arg")
    AUTH_KEY = sys.argv[1]
    start = datetime(2020, 4, 1)
    end = datetime(2022, 3, 20)

    fig, _ = plot_views_per_week(start, end, AUTH_KEY)
    fig.savefig("views-per-week.jpg")

    fig, _ = plot_all_time_bot_urls(start, end, AUTH_KEY)
    fig.savefig("bot-urls.jpg")

    fig, _ = plot_all_time_person_urls(start, end, AUTH_KEY)
    fig.savefig("person-urls.jpg")

    fig, _ = plot_all_time_bot_domains(start, end, AUTH_KEY)
    fig.savefig("bot-domains.jpg")

    fig, _ = plot_all_time_person_os(start, end, AUTH_KEY)
    fig.savefig("person-operating-systems.jpg")

    fig, _ = plot_all_time_person_devices(start, end, AUTH_KEY)
    fig.savefig("person-devices.jpg")

    fig, _ = plot_all_time_device_types(start, end, AUTH_KEY)
    fig.savefig("person-device-types.jpg")

    fig, _ = plot_all_time_person_browsers(start, end, AUTH_KEY)
    fig.savefig("person-browsers.jpg")

    bots_map = plot_bot_views_per_country(start, end, AUTH_KEY)
    bots_map.render_to_file("bots-map.svg")

    people_map = plot_person_views_per_country(start, end, AUTH_KEY)
    people_map.render_to_file("people-map.svg")
