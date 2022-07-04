import os.path

from datetime import datetime

import tables

from sapphire import download_coincidences

DATASTORE = "/Users/arne/Datastore/check_reconstructions"
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def download_sciencepark_coincidences():
    """Download a dataset for analysis

    This script downloads coincidence data from the Science Park stations.
    Station 507 is excluded because its detector positions are not well known.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences with many events (6+ or 7+) will be reconstructed.
    Note: Station 510 'overlaps' with 501.

    """
    start = (2015, 11)
    end = (2016, 2)
    stations = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]
    path = os.path.join(DATASTORE, 'dataset_sciencepark_n10_151101_160201.h5')
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt, end=enddt, n=10)


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
        yield (datetime(start[0], start[1], 1), datetime(start[0], start[1] + 1, 1))
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
            yield (datetime(current_year, current_month, 1), datetime(next_year, next_month, 1))

            current_year = next_year
            current_month = next_month
        return


if __name__ == "__main__":
    download_sciencepark_coincidences()
