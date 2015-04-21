""" Time between triggers

This creates a histogram of the time between subsequent triggers for
a station.

"""
import datetime
import os

import matplotlib.pyplot as plt
import tables
import numpy

from sapphire.api import Station


ESD_PATH = '/Users/arne/Datastore/esd'


def main(station_id=501, date=datetime.date(2013, 8, 1)):
    filepath = os.path.join(ESD_PATH, date.strftime('%Y/%-m/%Y_%-m_%-d.h5'))
    file = tables.openFile(filepath, 'r')
    station = Station(station_id)
    events = file.getNode('/hisparc/cluster_%s/station_%d/' %
                          (station.cluster.lower(), station_id), 'events')
    ext_timestamps = events.col('ext_timestamp')
    ext_timestamps.sort()
    difs = ext_timestamps[1:] - ext_timestamps[:-1]

    print ('Minimum: %d. Maximum: %d. n(diff < 100 us): %d' %
           (min(difs), max(difs), len(numpy.where(difs < 100000)[0])))

    bins = numpy.logspace(0, 11)
    plt.figure()
    plt.hist(difs, bins=bins)
    plt.xscale('log')
    plt.xlabel('Time between subsequent triggers (ns)')
    plt.ylabel('Occurance')
    plt.title('Time between triggers')
    plt.show()


if __name__=="__main__":
    main(station_id=501)
    main(station_id=502)
    main(station_id=503)
    main(station_id=504)
    main(station_id=505)
    main(station_id=506)
    main(station_id=508)
    main(station_id=103)
    main(station_id=102)
    main(station_id=7301)
