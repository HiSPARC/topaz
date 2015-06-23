#!/usr/bin/env python
import os
import sys
from datetime import date, timedelta

import matplotlib.pyplot as plt
import numpy

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

from django_publicdb.inforecords.models import Station
from django_publicdb.api.views import num_events_day


def main():
    stations = Station.objects.filter(pc__is_test=False)
    start_datum = date(2009, 1, 1)
    end_datum = date.today()

    station_ids = []
    # station_ids = [station.number for station in stations]
    data = []

    for station in stations:
        station_ids.append(station.number)
        nevents = []
        for datum in daterange(start_datum, end_datum):
            nevents.append(int(num_events_day('req', station.number,
                                              datum.year, datum.month,
                                              datum.day).content))
        data.append(nevents)
        print 'got data for %d' % station.number

    plt.figure(figsize=(16, 11))
    plt.imshow(data, interpolation='nearest', cmap=plt.get_cmap('Greys'),
               vmin=0, vmax=100000)

    plt.yticks(arange(len(station_ids)), station_ids, size='xx-small')

    year_range = range(start_datum.year, end_datum.year + 1)
    x_ticks = [(date(year, 1, 1) - start_datum).days for year in year_range]
    plt.xticks(x_ticks, year_range, size='xx-small')

    plt.title("Number of events per day between %s and %s, scale: 0-7e4" %
              (start_datum, end_datum))

    plt.savefig('/tmp/all_stations_n_events_day.pdf')


def daterange(start, stop):
    """Generator for date ranges

    This is a generator for date ranges. Based on a start and stop value,
    it generates one day intervals, from start upto but not including stop.

    :param start: a date instance
    :param stop: a date instance

    :yield date: one day intervals between start and stop
    """
    if start > stop:
        raise ValueError('start is bigger than stop')
    if start == stop:
        yield start
        return
    else:
        yield start
        cur = start
        cur += datetime.timedelta(days=1)
        while cur < stop:
            yield cur
            cur += datetime.timedelta(days=1)
        return


if __name__=="__main__":
    main()
