import os
import urllib.request, urllib.parse, urllib.error

from sapphire import Network
from sapphire.utils import pbar

BASE = 'http://data.hisparc.nl/show/source/eventtime/%d/'
PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/'


if __name__ == "__main__":
    station_numbers = Network().station_numbers()

    for sn in pbar(station_numbers):
        path = PATH + '%d.tsv' % sn
        if not os.path.exists(path):
            urllib.request.urlretrieve(BASE % sn, path)
