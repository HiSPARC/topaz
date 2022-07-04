"""Check for baseline offsets

    This script goes through all events tables from a raw data file. For
    each of these the baselines will be read and the average over the
    data will be calculated. Then the 'correct baseline' (200 ADC) is
    subtracted to see how much the baseline deviates from the correct
    value.

"""

import datetime
import os

import numpy
import tables

DATASTORE = '/Users/arne/Datastore/'


def get_baseline_offsets(date):
    """Read baselines from a data file

    Determine the mean of the baselines for each detector
    for each station with event data.

    """
    offsets = {}
    datapath = os.path.join(DATASTORE, date.strftime('%Y/%-m/%Y_%-m_%-d.h5'))
    with tables.open_file(datapath, 'r') as data:
        for node in data.walk_nodes('/hisparc'):
            if node._v_name == 'events':
                baselines = node.col('baseline')
                average_baselines = [int(round(mean_baseline - 200, 0))
                                     for mean_baseline in numpy.mean(baselines, 0)
                                     if not mean_baseline == -1]
                station_number = int(node._v_parent._v_name[8:])
                offsets[station_number] = average_baselines
    return offsets


def stations_with_large_offset(offsets):
    """Get stations where an average baseline has a large offset"""
    stations = sorted(station for station, baselines in offsets.items()
                       if numpy.max(numpy.abs(baselines)) > 5)
    return stations


if __name__ == '__main__':
    date = datetime.date(2013, 11, 5)
    offsets = get_baseline_offsets(date)
    # print offsets
    stations = stations_with_large_offset(offsets)
    print(stations)
