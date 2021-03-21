import requests
import datetime
import matplotlib.pyplot as plt
'''
Makes a request and plots the results.
Super quickly coded and will need to be revisited.
'''

# params = {'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Firefox'}
# r = requests.post('http://127.0.0.1:5000/report_traffic', params=params)


def parse_timeboxed_data(_json) -> ([datetime.datetime], [int], [int]):
    dates = []
    user = []
    bot = []
    for row in _json:
        # Format: "Mon, 05 Oct 2020 00:00:00 GMT"
        dates.append(datetime.datetime.strptime(row['date'], '%a, %d %b %Y %H:%M:%S %Z'))
        user.append(row['user'])
        bot.append(row['bot'])
    return dates, user, bot


def make_plot(
        dates: [datetime.datetime],
        user_data: [int],
        bot_data: [int],
        title: str,
        x_label: str = None,
        y_label: str = None,
):
    """Creates and returns a Pyplot figure for the given data."""
    fig, ax = plt.subplots()
    fig.suptitle(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.plot(dates, user_data, label='Users', linestyle='--')
    ax.plot(dates, bot_data, label='Bots', linestyle='--')
    ax.grid(True)
    fig.legend()
    return fig


# Make request, providing auth key
params = {'start_date': '2020-10-10', 'end_date': '2021-3-15'}
r = requests.get(
    'http://127.0.0.1:5000/api/v1/data/unique-ips-per-week',
    headers={'Authorization': 'dev'},
    params=params,
)
if r.status_code == 401:
    raise ValueError('Authentication failed')

dates, user_data, bot_data = parse_timeboxed_data(r.json())
fig = make_plot(dates, user_data, bot_data, 'Unique IP Addresses per Week', x_label='Week')
fig.show()


