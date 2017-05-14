import os

from datetime import datetime

from tables import open_file

from sapphire import esd

STATIONS = [501, 510, 99]
DATA_PATH = '/Users/arne/Datastore/'


def download_data(station):
    """Download data for the mounlab test

    - First the test with the lower detector placed in the HiSPARC office
    - Second the test with the lower detector placed in the Nikhef courtyard

    """
    path = os.path.join(DATA_PATH, 'muonlab_test.h5')
    with open_file(path, 'a') as data:
        # Two ranges since the muonlab station was offline part of the time
        esd.download_data(data, '/station_%d' % station, station,
                          datetime(2015, 5, 28, 15), datetime(2015, 5, 29, 9))
        esd.download_data(data, '/station_%d' % station, station,
                          datetime(2015, 6, 1, 8), datetime(2015, 6, 2, 11))

    path = os.path.join(DATA_PATH, 'muonlab_test2.h5')
    with open_file(path, 'a') as data:
        esd.download_data(data, '/station_%d' % station, station,
                          datetime(2015, 6, 2, 12), datetime(2015, 6, 16))

    path = os.path.join(DATA_PATH, 'muonlab_test3.h5')
    with open_file(path, 'a') as data:
        esd.download_data(data, '/station_%d' % station, station,
                          datetime(2015, 6, 2, 18), datetime(2015, 6, 25, 15))


if __name__ == "__main__":
    for station in STATIONS:
        download_data(station)
