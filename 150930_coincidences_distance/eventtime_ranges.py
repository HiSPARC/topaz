from numpy import arange, array, zeros

from sapphire import Station


def get_data(station_numbers):
    """Read the eventtime csv files for the given station numbers"""

    return {number: Station(number, force_stale=True).event_time()
            for number in station_numbers}


def get_total_exposure(timestamp_ranges):
    """Get total exposure time of the timestamp ranges"""

    if not len(timestamp_ranges):
        return 0.
    timestamp_ranges = array(timestamp_ranges)
    total_exposure = (timestamp_ranges[:, 1] - timestamp_ranges[:, 0]).sum()
    return total_exposure


def get_timestamp_ranges(station_numbers, min_n=None):
    """Get timestamp ranges where all stations have data

    :param station_numbers: list of station numbers that should be considered.
    :param min_n: if given at least this number of stations should have data,
                  for a date to be included.
    :return: list of timestamp range, using the following format:
             `[(start, end), (start, end), (start, end), ...]`

    """
    if min_n is None:
        min_n = len(station_numbers)
    data = get_data(station_numbers)

    first = min(values['timestamp'][0] for values in list(data.values()))
    last = max(values['timestamp'][-1] for values in list(data.values()))

    timestamps = arange(first, last + 1, 3600)
    extended_data = zeros((len(list(data.keys())), (last - first) / 3600 + 1))

    for i, sn in enumerate(data.keys()):
        start = (data[sn]['timestamp'][0] - first) / 3600
        end = start + len(data[sn])
        extended_data[i, start:end] = ((data[sn]['counts'] > 500) &
                                       (data[sn]['counts'] < 5000))

    flags = extended_data.sum(axis=0) >= min_n
    timestamp_ranges = get_ranges(timestamps, flags)
    return timestamp_ranges


def get_ranges(timestamps, flags):
    """Make timestamp ranges from timestamps list

    :param timestamps: list of timestamps.
    :param flags: list of flags (booleans) which indicate if all of the
                  requested stations have data during that timestamp..

    Inspired by http://stackoverflow.com/a/16315498/1033535

    """
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
