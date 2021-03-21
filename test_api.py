import requests
import datetime
import matplotlib.pyplot as plt


# params = {'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Firefox'}
# r = requests.post('http://127.0.0.1:5001/report_traffic', params=params)


params = {'start_date': '2020-10-10', 'end_date': '2021-3-15'}
r = requests.get('http://127.0.0.1:5000/api/v1/data/unique-users', params=params)
dates = []
user = []
bot = []
for row in r.json():
    # Format: "Mon, 05 Oct 2020 00:00:00 GMT"
    dates.append(datetime.datetime.strptime(row['date'], '%a, %d %b %Y %H:%M:%S %Z'))
    user.append(row['user'])
    bot.append(row['bot'])


fig, ax = plt.subplots()
fig.suptitle('Unique IP Addresses per Week')
ax.set_xlabel('Week')
ax.plot(
    dates,
    user,
    label='Users',
    linestyle='--',
)
ax.plot(
    dates,
    bot,
    label='Bots',
    linestyle='--',
)
ax.grid(True)
fig.legend()
fig.show()
