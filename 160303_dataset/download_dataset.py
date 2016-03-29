import os.path
from datetime import datetime
import multiprocessing

import tables

from sapphire import download_coincidences, download_data


DATASTORE = "/Users/arne/Datastore/dataset"
STATION_PATH = os.path.join(DATASTORE, 'dataset_s%d_110601_160201.h5')
COIN_PATH = os.path.join(DATASTORE, 'dataset_sciencepark_n2_110601_160201.h5')
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]
START = (2011, 6)
END = (2016, 2)


def download_sciencepark_station_data():
    worker_pool = multiprocessing.Pool(4)
    worker_pool.map(download_data_for_station, STATIONS)
    worker_pool.close()
    worker_pool.join()


def download_data_for_station(station_number):
    path = STATION_PATH % station_number
    if os.path.exists(path):
        return path
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(START, END):
            print 'downloading', startdt.date(), enddt.date(), station_number
            download_data(data, '/s%d' % station_number, station_number,
                          start=startdt, end=enddt,
                          type='events', progress=False)
    return path


def download_sciencepark_coincidences():
    """Download a dataset for analysis

    This script downloads coincidence data from the Science Park stations.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of station offsets.
    After this coincidences with many events (6+ or 7+) will be reconstructed.
    Note: Station 510 'overlaps' with 501. Station 507 is excluded.

    """
    path = COIN_PATH
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(START, END):
            download_coincidences(data, stations=STATIONS,
                                  start=startdt, end=enddt, n=2)


def monthrange(start, stop):
    """Generator for datetime month ranges

    This is a very specific generator for datetime ranges. Based on
    start and stop values, it generates one month intervals.

    :param start: a year, month tuple
    :param stop: a year, month tuple

    The stop is the last end of the range.

    """
    startdt = datetime(start[0], start[1], 1)
    stopdt = datetime(stop[0], stop[1], 1)

    if stopdt < startdt:
        return

    if start == stop:
        yield (datetime(start[0], start[1], 1),
               datetime(start[0], start[1] + 1, 1))
        return
    else:
        current_year, current_month = start

        while (current_year, current_month) != stop:
            if current_month < 12:
                next_year = current_year
                next_month = current_month + 1
            else:
                next_year = current_year + 1
                next_month = 1
            yield (datetime(current_year, current_month, 1),
                   datetime(next_year, next_month, 1))

            current_year = next_year
            current_month = next_month
        return


if __name__ == "__main__":
#     download_data_for_station(501)
    download_sciencepark_station_data()
    download_sciencepark_coincidences()
