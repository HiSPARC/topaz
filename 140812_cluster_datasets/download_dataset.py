import os.path

from datetime import datetime

import tables

from sapphire import download_coincidences

DATASTORE = "/Users/arne/Datastore/esd_coincidences"


def download_sciencepark_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Science Park stations.
    Station 507 is excluded because its detector positions are not well known.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences with many events (6+ or 7+) will be reconstructed.
    Note: Station 510 'overlaps' with 501.

    """
    stations = [501, 502, 503, 504, 505, 506, 508, 509, 510]
    path = os.path.join(DATASTORE, 'sciencepark_n2_100101_150401.h5')
    print("Downloading Science Park dataset.")
    with tables.open_file(path, 'a') as data:
        download_coincidences(data, stations=stations,
                              start=datetime(2010, 1, 1),
                              end=datetime(2015, 4, 1), n=2)


def download_sciencepark_dataset_n7():
    """Download a dataset for analysis

    This script downloads coincidence data from the Science Park stations.
    Station 507 is excluded because its detector positions are not well known.
    Coincidences with at least 7 events in a coincidence are included.
    Note: Station 510 'overlaps' with 501.

    """
    stations = [501, 502, 503, 504, 505, 506, 508, 509, 510]
    start = (2012, 1)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'sciencepark_n7_120101_150401.h5')
    print("Downloading n7 Science Park dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=7)


def download_aarhus_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Aarhus stations.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences that include each station will be reconstructed.

    """
    stations = [20001, 20002, 20003]
    start = (2012, 1)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'aarhus_n2_120101_140801.h5')
    print("Downloading Aarhus dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=2)


def download_zaanlands_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Zaanland stations.
    Three 2-detector stations, all on the roof of the Zaanlands Lyceum.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences that include each station will be reconstructed.

    """
    stations = [102, 104, 105]
    start = (2012, 6)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'zaanlands_n2_120601_140801.h5')
    print("Downloading Zaanlands dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=2)


def download_twente_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Twente stations.
    Three 2-detector stations, all on the roof of the TU Carre building.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences that include each station will be reconstructed.

    """
    stations = [7001, 7002, 7003]
    start = (2011, 8)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'twente_n2_110801_140801.h5')
    print("Downloading Twente dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=2)


def download_eindhoven_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Eindhoven stations.
    Four 2-detector stations, on the roofs of Universiteit Eindhoven.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    After this coincidences that include at least three station will be
    reconstructed.

    """
    stations = [8001, 8004, 8008, 8009]
    start = (2011, 10)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'eindhoven_n2_111001_140801.h5')
    print("Downloading Eindhoven dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=2)


def download_alphen_dataset():
    """Download a dataset for analysis

    This script downloads coincidence data from the Alphen ad Rijn stations.
    Three 2-detector stations, on high schools forming a triangle.
    Coincidences with at least 2 events in a coincidence are included.
    This allows for determination of detector and station offsets.
    These stations are far appart, so few coincidences are found that
    include all three stations. Using a larger coincidence window may help.

    """
    stations = [3301, 3302, 3303]
    start = (2010, 12)
    end = (2015, 4)
    path = os.path.join(DATASTORE, 'alphen_n2_101201_140801.h5')
    print("Downloading Alphen ad Rijn dataset.")
    with tables.open_file(path, 'a') as data:
        for startdt, enddt in monthrange(start, end):
            download_coincidences(data, stations=stations, start=startdt,
                                  end=enddt, n=2)


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
    download_alphen_dataset()
    download_eindhoven_dataset()
    download_aarhus_dataset()
    download_zaanlands_dataset()
    download_twente_dataset()
    download_sciencepark_dataset()
