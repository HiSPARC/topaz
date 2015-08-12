import urllib

from sapphire import Network

BASE = 'http://data.hisparc.nl/show/source/eventtime/%d/'

station_numbers = Network().station_numbers()

for sn in station_numbers:
    urllib.urlretrieve(BASE % sn, '%d.csv' % sn)
