import requests
import datetime
import matplotlib.pyplot as plt


# params = {'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Firefox'}
# r = requests.post('http://127.0.0.1:5001/report_traffic', params=params)


params = {'start_date': '2020-10-10', 'end_date': '2021-3-15'}
r = requests.get('http://127.0.0.1:5000/api/v1/data/views', params=params)
dates = []
user = []
bot = []
for row in r.json():
    print(row['date'], row['user'], row['bot'])
    dates.append(row['date'])
    user.append(row['user'])
    bot.append(row['bot'])


fig, ax = plt.subplots()
fig.suptitle('Unique IP Addresses per Week')
ax.set_xlabel('Week')
# ax.set_ylabel('New Unique Addresses')
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
# Rotate x-axis ticks to avoid cramping
ax.tick_params(axis='x', labelrotation=20)
# Only plotting one portfolio: place legend in "best" position
# (usually upper-right)
fig.legend()
fig.show()