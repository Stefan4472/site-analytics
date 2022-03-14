import requests
import pygal
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
"""Quick script to make API requests and create plots."""


def make_request(params: dict, auth_key: str) -> List:
    r = requests.get(
        'http://127.0.0.1:5000/api/v1/data/statistics',
        headers={'Authorization': auth_key},
        params=params,
    )
    if r.status_code == 401:
        raise ValueError('Authentication failed')
    return r.json()


def parse_timeboxed_data(_json) -> ([datetime], [str], [int]):
    dates: List[datetime] = []
    keys: List[str] = []
    counts: List[int] = []
    for row in _json:
        # Format: "Mon, 05 Oct 2020 00:00:00 GMT"
        dates.append(datetime.strptime(row['date'], '%a, %d %b %Y %H:%M:%S %Z'))
        keys.append(row['key'])
        counts.append(row['quantity'])
    return dates, keys, counts


def plot_views_per_week(filename: str, auth_key: str):
    base_params = {
        'count_what': 'Views',
        'group_what': 'Nothing',
        'resolution': 'Week',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    bot_params = dict(base_params, query_on='Bots')
    bot_views_per_year = make_request(bot_params, auth_key)
    bdates, bkeys, bcounts = parse_timeboxed_data(bot_views_per_year)

    people_params = dict(base_params, query_on='People')
    people_views_per_year = make_request(people_params, auth_key)
    pdates, pkeys, pcounts = parse_timeboxed_data(people_views_per_year)

    fig, ax = plt.subplots()
    fig.suptitle('Views per Week')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Views')
    ax.plot(bdates, bcounts, label='Bots', linestyle='--')
    ax.plot(pdates, pcounts, label='People', linestyle='--')
    ax.grid(True)
    fig.legend()
    fig.savefig(filename)


# Map Geo-API country name to pygal country code
COUNTRY_CODE_MAPPING = {
    'Andorra': 'ad',
    'United Arab Emirates': 'ae',
    'Afghanistan': 'af',
    'Albania': 'al',
    'Armenia': 'am',
    'Angola': 'ao',
    'Antarctica': 'aq',
    'Argentina': 'ar',
    'Austria': 'at',
    'Australia': 'au',
    'Azerbaijan': 'az',
    'Bosnia and Herzegovina': 'ba',
    'Bangladesh': 'bd',
    'Belgium': 'be',
    'Burkina Faso': 'bf',
    'Bulgaria': 'bg',
    'Bahrain': 'bh',
    'Burundi': 'bi',
    'Benin': 'bj',
    'Brunei Darussalam': 'bn',
    'Bolivia, Plurinational State of': 'bo',
    'Brazil': 'br',
    'Bhutan': 'bt',
    'Botswana': 'bw',
    'Belarus': 'by',
    'Belize': 'bz',
    'Canada': 'ca',
    'Congo, the Democratic Republic of the': 'cd',
    'Central African Republic': 'cf',
    'Congo': 'cg',
    'Switzerland': 'ch',
    'Ivory Coast': 'ci',
    'Chile': 'cl',
    'Cameroon': 'cm',
    'China': 'cn',
    'Colombia': 'co',
    'Costa Rica': 'cr',
    'Cuba': 'cu',
    'Cape Verde': 'cv',
    'Cyprus': 'cy',
    'Czechia': 'cz',
    'Germany': 'de',
    'Djibouti': 'dj',
    'Denmark': 'dk',
    'Dominican Republic': 'do',
    'Algeria': 'dz',
    'Ecuador': 'ec',
    'Estonia': 'ee',
    'Egypt': 'eg',
    'Western Sahara': 'eh',
    'Eritrea': 'er',
    'Spain': 'es',
    'Ethiopia': 'et',
    'Finland': 'fi',
    'France': 'fr',
    'Gabon': 'ga',
    'United Kingdom': 'gb',
    'Georgia': 'ge',
    'French Guiana': 'gf',
    'Ghana': 'gh',
    'Greenland': 'gl',
    'Gambia': 'gm',
    'Guinea': 'gn',
    'Equatorial Guinea': 'gq',
    'Greece': 'gr',
    'Guatemala': 'gt',
    'Guam': 'gu',
    'Guinea-Bissau': 'gw',
    'Guyana': 'gy',
    'Hong Kong': 'hk',
    'Honduras': 'hn',
    'Croatia': 'hr',
    'Haiti': 'ht',
    'Hungary': 'hu',
    'Indonesia': 'id',
    'Ireland': 'ie',
    'Israel': 'il',
    'India': 'in',
    'Iraq': 'iq',
    'Iran, Islamic Republic of': 'ir',
    'Iceland': 'is',
    'Italy': 'it',
    'Jamaica': 'jm',
    'Jordan': 'jo',
    'Japan': 'jp',
    'Kenya': 'ke',
    'Kyrgyzstan': 'kg',
    'Cambodia': 'kh',
    'Korea Korea': 'kp',
    'South Korea': 'kr',
    'Kuwait': 'kw',
    'Kazakhstan': 'kz',
    'Lao People’s Democratic Republic': 'la',
    'Lebanon': 'lb',
    'Liechtenstein': 'li',
    'Sri Lanka': 'lk',
    'Liberia': 'lr',
    'Lesotho': 'ls',
    'Lithuania': 'lt',
    'Luxembourg': 'lu',
    'Latvia': 'lv',
    'Libyan Arab Jamahiriya': 'ly',
    'Morocco': 'ma',
    'Monaco': 'mc',
    'Moldova, Republic of': 'md',
    'Montenegro': 'me',
    'Madagascar': 'mg',
    'North Macedonia': 'mk',
    'Mali': 'ml',
    'Myanmar': 'mm',
    'Mongolia': 'mn',
    'Macao': 'mo',
    'Mauritania': 'mr',
    'Malta': 'mt',
    'Mauritius': 'mu',
    'Maldives': 'mv',
    'Malawi': 'mw',
    'Mexico': 'mx',
    'Malaysia': 'my',
    'Mozambique': 'mz',
    'Namibia': 'na',
    'Niger': 'ne',
    'Nigeria': 'ng',
    'Nicaragua': 'ni',
    'Netherlands': 'nl',
    'Norway': 'no',
    'Nepal': 'np',
    'New Zealand': 'nz',
    'Oman': 'om',
    'Panama': 'pa',
    'Peru': 'pe',
    'Papua New Guinea': 'pg',
    'Philippines': 'ph',
    'Pakistan': 'pk',
    'Poland': 'pl',
    'Puerto Rico': 'pr',
    'Palestine, State of': 'ps',
    'Portugal': 'pt',
    'Paraguay': 'py',
    'Reunion': 're',
    'Romania': 'ro',
    'Serbia': 'rs',
    'Russia': 'ru',
    'Rwanda': 'rw',
    'Saudi Arabia': 'sa',
    'Seychelles': 'sc',
    'Sudan': 'sd',
    'Sweden': 'se',
    'Singapore': 'sg',
    'Saint Helena, Ascension and Tristan da Cunha': 'sh',
    'Slovenia': 'si',
    'Slovakia': 'sk',
    'Sierra Leone': 'sl',
    'San Marino': 'sm',
    'Senegal': 'sn',
    'Somalia': 'so',
    'Suriname': 'sr',
    'Sao Tome and Principe': 'st',
    'El Salvador': 'sv',
    'Syrian Arab Republic': 'sy',
    'Swaziland': 'sz',
    'Chad': 'td',
    'Togo': 'tg',
    'Thailand': 'th',
    'Tajikistan': 'tj',
    'Timor-Leste': 'tl',
    'Turkmenistan': 'tm',
    'Tunisia': 'tn',
    'Turkey': 'tr',
    'Taiwan (Republic of China)': 'tw',
    'Tanzania, United Republic of': 'tz',
    'Ukraine': 'ua',
    'Uganda': 'ug',
    'United States': 'us',
    'Uruguay': 'uy',
    'Uzbekistan': 'uz',
    'Holy See (Vatican City State)': 'va',
    'Venezuela': 've',
    'Vietnam': 'vn',
    'Yemen': 'ye',
    'Mayotte': 'yt',
    'South Africa': 'za',
    'Zambia': 'zm',
    'Zimbabwe': 'zw',
}


def plot_views_per_country(filename: str, auth_key: str):
    base_params = {
        'count_what': 'Views',
        'group_what': 'Country',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }

    bot_params = dict(base_params, query_on='Bots')
    bot_views_by_country = make_request(bot_params, auth_key)
    # Filter out the '' country name (i.e., unknown)
    bcounts = {COUNTRY_CODE_MAPPING[data['key']]: data['quantity'] for data in bot_views_by_country if data['key'] != ''}
    bot_map = pygal.maps.world.World()
    bot_map.title = 'Number of Bot Views per Country, All Time'
    bot_map.add('All Time', bcounts)
    bot_map.render_to_file('bot-map.svg')

    people_params = dict(base_params, query_on='People')
    people_views_by_country = make_request(people_params, auth_key)
    pcounts = {COUNTRY_CODE_MAPPING[data['key']]: data['quantity'] for data in people_views_by_country if data['key'] != '' and data['key'] != 'Guernsey'}
    people_map = pygal.maps.world.World()
    people_map.title = 'Number of Human Views per Country, All Time'
    people_map.add('All Time', pcounts)
    people_map.render_to_file('people-map.svg')


def get_all_time_urls(auth_key: str):
    base_params = {
        'count_what': 'Views',
        'group_what': 'Url',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }

    bot_params = dict(base_params, query_on='Bots')
    bot_urls_all_time = make_request(bot_params, auth_key)
    bot_urls_all_time.sort(key=lambda x: x['quantity'], reverse=True)
    print(bot_urls_all_time)

    people_params = dict(base_params, query_on='People')
    people_urls_all_time = make_request(people_params, auth_key)
    people_urls_all_time.sort(key=lambda x: x['quantity'], reverse=True)
    print(people_urls_all_time)


def get_all_time_bot_domains(auth_key: str):
    """Bot domains by number of views, all time."""
    params = {
        'query_on': 'Bots',
        'count_what': 'Views',
        'group_what': 'Domain',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    bot_domains_all_time = make_request(params, auth_key)
    bot_domains_all_time.sort(key=lambda x: x['quantity'], reverse=True)
    print(bot_domains_all_time)


def plot_all_time_person_os(filename: str, auth_key: str):
    """Operating Systems by number of person-users, all time."""
    params = {
        'query_on': 'People',
        'count_what': 'Users',
        'group_what': 'OperatingSystem',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    people_os_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_os_all_time = \
        {'Android': 0, 'iOS': 0, 'Linux/Unix': 0, 'MAC': 0, 'Windows': 0, 'Other': 0}
    for data in people_os_all_time:
        if data['key'].startswith('Android'):
            binned_os_all_time['Android'] += data['quantity']
        elif data['key'].startswith('iOS'):
            binned_os_all_time['iOS'] += data['quantity']
        elif data['key'].startswith('Linux') or data['key'].startswith('Ubuntu'):
            binned_os_all_time['Linux/Unix'] += data['quantity']
        elif data['key'].startswith('Mac'):
            binned_os_all_time['MAC'] += data['quantity']
        elif data['key'].startswith('Windows'):
            binned_os_all_time['Windows'] += data['quantity']
        elif data['key'].startswith('Other'):
            binned_os_all_time['Other'] += data['quantity']
        else:
            print(data)

    fig, ax = plt.subplots()
    fig.suptitle('Person Operating Systems')
    ax.pie(binned_os_all_time.values(), labels=binned_os_all_time.keys())
    fig.savefig(filename)


def plot_all_time_person_devices(filename: str, auth_key: str):
    """Devices by number of person-users, all time."""
    params = {
        'query_on': 'People',
        'count_what': 'Users',
        'group_what': 'Device',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    people_devices_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_devices_all_time = {
        'Huawei': 0, 'Apple': 0, 'XiaoMi': 0, 'Samsung': 0, 'Google': 0,
        'Other Android': 0, 'Other': 0, 'Unknown': 0}
    for data in people_devices_all_time:
        if 'Huawei' in data['key']:
            binned_devices_all_time['Huawei'] += data['quantity']
        elif 'Apple' in data['key']:
            binned_devices_all_time['Apple'] += data['quantity']
        elif 'XiaoMi' in data['key']:
            binned_devices_all_time['XiaoMi'] += data['quantity']
        elif 'Samsung' in data['key']:
            binned_devices_all_time['Samsung'] += data['quantity']
        elif 'Android' in data['key']:
            binned_devices_all_time['Other Android'] += data['quantity']
        elif 'Google' in data['key']:
            binned_devices_all_time['Google'] += data['quantity']
        elif data['key'] == '' or 'Generic' in data['key']:
            binned_devices_all_time['Unknown'] += data['quantity']
        else:
            binned_devices_all_time['Other'] += data['quantity']

    fig, ax = plt.subplots()
    fig.suptitle('Person Device Manufacturers')
    ax.pie(binned_devices_all_time.values(), labels=binned_devices_all_time.keys())
    ax.legend()
    fig.savefig(filename)


def plot_all_time_device_types(filename: str, auth_key: str):
    """Devices by number of person-users, all time."""
    params = {
        'query_on': 'People',
        'count_what': 'Users',
        'group_what': 'DeviceType',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    people_devices_all_time = make_request(params, auth_key)
    values = [d['quantity'] for d in people_devices_all_time]
    labels = [d['key'] for d in people_devices_all_time]
    labels[labels.index('')] = 'Unknown'
    fig, ax = plt.subplots()
    fig.suptitle('Device Types')
    ax.pie(values, labels=labels)
    fig.savefig(filename)


def plot_all_time_person_browsers(filename: str, auth_key: str):
    """Browser by number of person-users, all time."""
    params = {
        'query_on': 'People',
        'count_what': 'Users',
        'group_what': 'Browser',
        'resolution': 'AllTime',
        'start_date': '2020-4-1',
        'end_date': '2022-5-1',
    }
    people_browsers_all_time = make_request(params, auth_key)
    # Standardize keys
    binned_browsers_all_time = {
        'Chrome': 0, 'Edge': 0, 'Firefox': 0, 'Safari': 0, 'Opera': 0, 'IE': 0, 'Http-Client': 0, 'Other': 0, 'Unknown': 0}
    for data in people_browsers_all_time:
        if 'Chrome' in data['key']:
            binned_browsers_all_time['Chrome'] += data['quantity']
        elif 'Edge' in data['key']:
            binned_browsers_all_time['Edge'] += data['quantity']
        elif 'Firefox' in data['key']:
            binned_browsers_all_time['Firefox'] += data['quantity']
        elif 'Safari' in data['key']:
            binned_browsers_all_time['Safari'] += data['quantity']
        elif 'Opera' in data['key']:
            binned_browsers_all_time['Opera'] += data['quantity']
        elif 'IE' in data['key']:
            binned_browsers_all_time['IE'] += data['quantity']
        elif 'Other' in data['key']:
            binned_browsers_all_time['Unknown'] += data['quantity']
        elif 'Http' in data['key'] or 'http' in data['key']:
            binned_browsers_all_time['Http-Client'] += data['quantity']
        else:
            binned_browsers_all_time['Other'] += data['quantity']
    print(binned_browsers_all_time)
    as_tuples = [(k, v) for k, v in binned_browsers_all_time.items()]
    as_tuples.sort(key=lambda x: x[1], reverse=True)
    labels = [t[0] for t in as_tuples]
    vals = [t[1] for t in as_tuples]
    print(labels)
    fig, ax = plt.subplots()
    fig.suptitle('Person Browsers')
    ax.pie(vals, labels=labels)
    fig.savefig(filename)


if __name__ == '__main__':
    AUTH_KEY = 'dev'

    # plot_views_per_week('views-per-week.jpg', AUTH_KEY)
    # plot_views_per_country('views-by-country.jpg', AUTH_KEY)
    # get_all_time_urls(AUTH_KEY)
    # get_all_time_bot_domains(AUTH_KEY)
    # plot_all_time_person_os('operating-systems.jpg', AUTH_KEY)
    # plot_all_time_person_devices('manufacturers.jpg', AUTH_KEY)
    # plot_all_time_device_types('devices.jpg', AUTH_KEY)
    plot_all_time_person_browsers('browsers.jpg', AUTH_KEY)