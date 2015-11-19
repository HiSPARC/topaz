"""Examine the intervals between triggers

Here we look at the intervals between consecutive triggers in a station.
The station should have data reduction and the mean filter disabled.
This is to look for overlapping traces. This means that the trace of the
second event should start less than 6 us after the first.

Todo: fix t_trigger reconstruction for station 501.

"""
from glob import glob
import os
import datetime

import tables

from artist import Plot

from sapphire import download_data


DATA_PATH = '/Users/arne/Datastore/trigger_interval/data.h5'
STATION = 501
STATION_GROUP = '/station_%d' % STATION


def download_dataset():
    with tables.open_file(DATA_PATH, 'w') as data:
        download_data(data, STATION_GROUP, STATION,
                      datetime.datetime(2015, 1, 1),
                      datetime.datetime(2015, 10, 1))

# Already downloaded:
# 1/2015 - 10/2015

def get_data():
    dt_event = []
    with tables.open_file(DATA_PATH, 'r') as data:
        try:
            events = data.get_node(STATION_GROUP, 'events')
        except tables.NoSuchNodeError:
            pass
        else:
            ext_ts = events.col('ext_timestamp')
            t_trig = events.col('t_trigger')
            dt_ext_timestamps = ext_ts[1:] - ext_ts[:-1]
            dt_t_trigger = t_trig[1:] - t_trig[:-1]
            dt_event.extend(dt_ext_timestamps - dt_t_trigger)
    return dt_event


def do_stuff(dt_event):
    sorted_dt_event = sorted(dt_event)
    print sorted_dt_event[:25]


if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        download_dataset()
    if 'dt_event' not in globals():
        dt_event = get_data()
    do_stuff(dt_event)

