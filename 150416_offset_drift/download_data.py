import os

from tables import open_file

from datetime import datetime
from sapphire import esd

STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 1006]
DATA_PATH = '/Users/arne/Datastore/esd/'


def download_monthly_data(station):
    """Download data from first day of each month"""
    for y in range(2010, 2016):
        for m in range(1, 13):
            if y == 2015 and m >= 4:
                continue
            path = os.path.join(DATA_PATH, '%d/%d/%d_%d_1.h5' % (y, m, y, m))
            with open_file(path, 'a') as data:
                esd.download_data(data, '/station_%d' % station, station,
                                  datetime(y, m, 1))


def download_daily_data(station):
    """Download data from each day for a month"""
    for d in range(2, 32):
        path = os.path.join(DATA_PATH, '2013/1/2013_1_%d.h5' % d)
        with open_file(path, 'a') as data:
            esd.download_data(data, '/station_%d' % station, station,
                              datetime(2013, 1, d))


if __name__ == "__main__":
    for station in STATIONS:
        download_monthly_data(station)
        download_daily_data(station)
