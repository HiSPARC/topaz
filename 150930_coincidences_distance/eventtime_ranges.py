from glob import glob
import os

from numpy import genfromtxt, zeros, histogram, arange


PATH = '/Users/arne/Datastore/publicdb_csv/eventtime/{station_number}.csv'


def read_eventtime(path):
    return genfromtxt(path, delimiter='\t', dtype=None,
                      names=['timestamp', 'counts'])


def get_data(station_numbers):
    return {number: read_eventtime(PATH.format(station_number=number))
            for number in station_numbers}


def get_timestamp_ranges(station_numbers):
    """Get timestamp ranges where all stations have data

    [(start, end), (start, end), (start, end), ...]

    """
    data = get_data(station_numbers)

    first = min(values['timestamp'][0] for values in data.values())
    last = max(values['timestamp'][-1] for values in data.values())

    timestamps = arange(first, last + 1, 3600)
    extended_data = zeros((len(data.keys()), (last - first) / 3600 + 1))

    for i, sn in enumerate(data.keys()):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        extended_data[i, start:end] = ((data[sn]['counts'] > 500) &
                                       (data[sn]['counts'] < 5000))

    flags = extended_data.sum(axis=0) == len(station_numbers)
    timestamp_ranges = get_ranges(timestamps, flags)
    return timestamp_ranges


def get_ranges(timestamps, flags):
    # Inspired by http://stackoverflow.com/a/16315498/1033535
    timestamp_ranges = []
    prev_flag = False
    for timestamp, flag in zip(timestamps, flags):
        if flag:
            # All stations have data
            if not timestamp_ranges or len(timestamp_ranges[-1]) == 2:
                # Start new range
                timestamp_ranges.append([timestamp])
        if prev_flag and not flag:
            # End of a range
            timestamp_ranges[-1].append(timestamp)
        prev_flag = flag
    if timestamp_ranges and len(timestamp_ranges[-1]) == 1:
        timestamp_ranges[-1].append(timestamps[-1] + 3600)

    return timestamp_ranges


if __name__ == "__main__":
    timestamp_ranges = get_timestamp_ranges([2, 3])
