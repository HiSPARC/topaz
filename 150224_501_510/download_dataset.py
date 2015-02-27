from datetime import datetime
import tables

from sapphire.esd import download_coincidences, download_data

PATH = '/Users/arne/Datastore/501_510/'


def download_501_510_dataset():
    """Download a dataset for analysis

    """
    print "Downloading 501-510 dataset."
    stations = [501, 510]

    start = datetime(2015, 1, 20)
    end = datetime(2015, 2, 1)

    with tables.open_file(PATH + 'c_501_510_150120_150201.h5', 'a') as data:
        download_coincidences(data, stations=stations, start=start, end=end,
                              n=2)
#
#     with tables.open_file(PATH + 'e_501_510_141101_150201.h5', 'a') as data:
#         for station in stations:
#             download_data(data, '/s%d' % station, station, start=start, end=end)


if __name__ == "__main__":
    download_501_510_dataset()
