import os

from tables import open_file

from datetime import datetime
from sapphire import esd

STATIONS = [501, 510, 99]
DATA_PATH = '/Users/arne/Datastore/'


def download_data(station):
    """Download data from first day of each month"""
    path = os.path.join(DATA_PATH, 'muonlab_test.h5')
    with open_file(path, 'a') as data:
        esd.download_data(data, '/station_%d' % station, station,
                          datetime(2015, 5, 28), datetime(2015, 6, 2))


if __name__ == "__main__":
    for station in STATIONS:
        download_data(station)
