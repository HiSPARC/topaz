""" Time between triggers

This creates a histogram of the time between subsequent triggers for
a station.

"""
import datetime
import os

import matplotlib.pyplot as plt
import tables
import numpy

from artist import Plot

from sapphire import Station


ESD_PATH = '/Users/arne/Datastore/esd'


def main(station_number=501, date=datetime.date(2013, 8, 1)):
    filepath = os.path.join(ESD_PATH, date.strftime('%Y/%-m/%Y_%-m_%-d.h5'))
    with tables.open_file(filepath, 'r') as data:
        station = Station(station_number)
        events = data.get_node('/hisparc/cluster_%s/station_%d/' %
                               (station.cluster.lower(), station_number),
                               'events')
        ext_timestamps = events.col('ext_timestamp')
    ext_timestamps.sort()
    difs = ext_timestamps[1:] - ext_timestamps[:-1]

    print ('Minimum: %d. Maximum: %d. n(diff < 100 us): %d' %
           (min(difs), max(difs), len(numpy.where(difs < 100000)[0])))

    bins = numpy.logspace(0, 11)
    plot = Plot('semilogx')
    plot.histogram(*numpy.histogram(difs, bins=bins))
    plot.set_xlabel('Time between subsequent triggers (ns)')
    plot.set_ylabel('Occurance')
    plot.save_as_pdf('time_between_triggers_%d' % station_number)


if __name__ == "__main__":
    for s in [501, 502, 503, 504, 505, 506, 508, 102, 103, 7301]:
        main(station_number=s)
