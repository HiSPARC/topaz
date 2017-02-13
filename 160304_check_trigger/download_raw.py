import datetime

import tables

from sapphire.publicdb import download_data


if __name__ == "__main__":
    start = datetime.datetime(2015, 6, 3)
    end = datetime.datetime(2015, 6, 4)
    with tables.open_file('/Users/arne/Datastore/check_trigger/data.h5', 'w') as data:
        download_data(data, '/s501', 501, start, end, get_blobs=True)

    start = datetime.datetime(2012, 6, 10)
    end = datetime.datetime(2012, 6, 11)
    with tables.open_file('/Users/arne/Datastore/check_trigger/data_502_1.h5', 'w') as data:
        download_data(data, '/s502', 502, start, end, get_blobs=True)

    start = datetime.datetime(2012, 8, 1)
    end = datetime.datetime(2012, 8, 2)
    with tables.open_file('/Users/arne/Datastore/check_trigger/data_502_2.h5', 'w') as data:
        download_data(data, '/s502', 502, start, end, get_blobs=True)
