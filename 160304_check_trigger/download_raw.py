import datetime

import tables

from sapphire.publicdb import download_data


if __name__ == "__main__":
    start = datetime.datetime(2015, 6, 3)
    end = datetime.datetime(2015, 6, 4)
    with tables.open_file('data.h5', 'w') as data:
        download_data(data, '/s501', 501, start, end, get_blobs=True)
