from datetime import datetime
import tables

from sapphire import download_coincidences, download_data


def download_501_510_dataset():
    """Download a dataset for analysis

    """
    print "Downloading 501-510 dataset."
    stations = [501, 510]

    start = datetime(2014, 10, 1)
    end = datetime(2014, 10, 10)

    with tables.open_file('/Users/arne/Datastore/501_510/c_501_510_141001_141011.h5', 'a') as data:
        download_coincidences(data, stations=stations, start=start, end=end, n=2)

    with tables.open_file('/Users/arne/Datastore/501_510/e_501_510_141001_141011.h5', 'a') as data:
        download_data(data, '/s501', 501, start=start, end=end)
        download_data(data, '/s510', 510, start=start, end=end)

    start = datetime(2014, 11, 1)
    end = datetime(2014, 11, 10)

    with tables.open_file('/Users/arne/Datastore/501_510/c_501_510_141101_141111.h5', 'a') as data:
        download_coincidences(data, stations=stations, start=start, end=end, n=2)

    with tables.open_file('/Users/arne/Datastore/501_510/e_501_510_141101_141111.h5', 'a') as data:
        download_data(data, '/s501', 501, start=start, end=end)
        download_data(data, '/s510', 510, start=start, end=end)


if __name__ == "__main__":
    download_501_510_dataset()
