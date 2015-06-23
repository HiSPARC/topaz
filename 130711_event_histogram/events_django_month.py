#!/usr/bin/env python
import os
import sys
from datetime import date, timedelta

from pylab import imshow, show, yticks, savefig

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

from django_publicdb.inforecords.models import Station
from django_publicdb.api.views import num_events_month
from numpy import *


def main():
    stations = Station.objects.filter(pc__is_test=False)
    station_ids = []

    years = arange(2004, 2014)
    months = arange(12) + 1

    data = []

    for station in stations:
        station_ids.append(station['number'])
        nevents = []
        for year in years:
            for month in months:
                if year == 2013 and month > 7:
                    continue
                nevents.append(int(num_events_month('req', station['number'], year, month).content))
        data.append(nevents)
        print 'got data for %d' % station['number']

    imshow(data, interpolation='nearest', cmap=plt.get_cmap('Greys'), vmin=0, vmax=2e6)
    show()
    yticks(arange(len(station_ids)), station_ids, size='xx-small')
    xticks((years - years[0]) * 12, years, size='xx-small')
    title("Number of events per month between %d and %d, scale: 0-2e6" % (years[0], year[-1]))

    savefig('/tmp/all_station_n_events_month.pdf',
            facecolor='none', edgecolor='none')

if __name__=="__main__":
    main()
