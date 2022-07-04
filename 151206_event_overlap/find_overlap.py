""" Look for overlap in event traces

On 151204 I ran some tests with station 510, using HiSPARC III electronics,
and Firmware 19 and a new test version which should fix misaligned traces.
Pulses were simulated using a pulse generator.

I was not able to reproduce the misaligned traces seen in 150522_dead_time.

This script downloads the relevant data and looks for the size of the overlap
in the traces.

"""
import os

from datetime import datetime

import tables

from numpy import array

from sapphire import Station, download_data

DATA = '/Users/arne/Datastore/event_overlap.h5'


def get_data():
    if os.path.exists(DATA):
        print('data already exists')
        return
    with tables.open_file(DATA, 'w') as data:
        download_data(data, '/s99', 99, datetime(2015, 12, 4))


def find_overlaps():
    with tables.open_file(DATA, 'r') as data:
        events = data.root.s99.events
        s = Station(99)
        for i in range(events.nrows - 1):
            if events[i + 1]['ext_timestamp'] - events[i]['ext_timestamp'] > 1e4:
                continue
            t1 = s.event_trace(events[i]['timestamp'], events[i]['nanoseconds'], True)
            t2 = s.event_trace(events[i + 1]['timestamp'], events[i + 1]['nanoseconds'], True)
            overlap = longest_overlap(t1[0], t2[0])
            if overlap is not None:
                print(i, len(overlap) * 2.5, 'ns')
            else:
                print(i, 'No overlap')


def longest_overlap(a, b):
    """Find longest overlap between two lists

    Idea from http://mathematica.stackexchange.com/a/77877

    Find the longest common sublists which is at the end of list a and
    the start of list b.

    :param a,b: the lists to compare.
    :return: the overlapping sublist.

    """
    a = array(a)
    b = array(b)
    if len(a) <= len(b):
        max_length = len(a)
    else:
        max_length = len(b)
    for i in range(max_length):
        if all(a[-max_length + i:] == b[:max_length - i]):
            return a[-max_length + i:]


if __name__ == "__main__":
    get_data()
    find_overlaps()
