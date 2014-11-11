from sapphire import api
from datetime import date, timedelta

start = date(2014, 9, 10)
yesterday = date.today() - timedelta(days=1)

s = api.Station(23)
events = [0]*24
while start < yesterday:
    start += timedelta(days=1)
    for i in range(24):
        events[i] += s.n_events(start.year, start.month, start.day, i)

plot(range(24), events)
