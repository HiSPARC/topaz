import datetime
import os
import zlib

import tables

from numpy import arange, histogram, histogram2d, linspace, log10, where

from artist import Plot

from sapphire import Station
from sapphire.analysis.process_events import ProcessEventsWithTriggerOffset
from sapphire.analysis.process_traces import MeanFilter
from sapphire.publicdb import download_data

DATA_PATH = '/Users/arne/Datastore/ttrigger_filter/data.h5'
STATION = 505
GROUP = '/s%d' % STATION
API_STATION = Station(STATION)
COLORS = ['black', 'red', 'green', 'blue']


class ProcessEventsWithFilteredTraces(ProcessEventsWithTriggerOffset):

    """Filter the traces before extracting data from them

    To be used with data for which the noise filter was disabled.

    :param data: the PyTables datafile
    :param group: the group containing the station data.  In normal
        cases, this is simply the group containing the events table.
    :param source: the name of the events table.  Default: None,
        meaning the default name 'events'.
    :param progress: if True show a progressbar while copying and
                     processing events.
    :param station: station number of station to which the data belongs.

    """

    def _get_trace(self, idx):
        """Returns a trace given an index into the blobs array.

        Decompress a trace from the blobs array.

        :param idx: index into the blobs array
        :return: iterator over the pulseheight values

        """
        blobs = self._get_blobs()

        try:
            trace = zlib.decompress(blobs[idx]).split(',')
        except zlib.error:
            trace = zlib.decompress(blobs[idx][1:-1]).split(',')
        if trace[-1] == '':
            del trace[-1]
        trace = [int(x) for x in trace]

        filtered_trace = MeanFilter().filter_trace(trace)

        return iter(filtered_trace)


def get_data():
    """Ensure data is downloaded and available"""

    if not os.path.exists(DATA_PATH):
        with tables.open_file(DATA_PATH, 'w') as data:
            start = datetime.datetime(2014, 6, 10)
            end = datetime.datetime(2014, 6, 11)
            download_data(data, GROUP, STATION, start, end, get_blobs=True)


def process_data():
    """Process data with filtered and unfiltered traces"""
    with tables.open_file(DATA_PATH, 'a') as data:
        try:
            pe = ProcessEventsWithTriggerOffset(data, GROUP, station=STATION)
            pe.process_and_store_results('events_processed', overwrite=False, limit=10000)
        except RuntimeError:
            pass
        try:
            pe = ProcessEventsWithFilteredTraces(data, GROUP, station=STATION)
            pe.process_and_store_results('events_filtered', overwrite=False, limit=10000)
        except RuntimeError:
            pass


def compare_ttrigger():
    with tables.open_file(DATA_PATH, 'r') as data:
        processed = data.get_node(GROUP, 'events_processed')
        filtered = data.get_node(GROUP, 'events_filtered')

        assert all(processed.col('ext_timestamp') == filtered.col('ext_timestamp'))

        trig_proc = processed.col('t_trigger')
        trig_filt = filtered.col('t_trigger')
        dt_trigger = trig_filt - trig_proc

        density = (processed.col('n1') + processed.col('n2') +
                   processed.col('n3') + processed.col('n4')) / 2
        print 'Density range:', density.min(), density.max()
        print 'dt trigger range:', dt_trigger.min(), dt_trigger.max()

        if len(trig_proc) > 4000:
            plot = Plot()
            bins = [linspace(0, 30, 100), arange(-11.25, 75, 2.5)]
            c, x, y = histogram2d(density, dt_trigger, bins=bins)
            # plot.histogram2d(c, x, y, bitmap=True, type='color', colormap='viridis')
            plot.histogram2d(log10(c + 0.01), x, y, type='area')
            plot.set_xlabel('Particle density')
            plot.set_ylabel('Difference in trigger time')
            plot.save_as_pdf('hist2d')
        else:
            plot = Plot()
            plot.scatter(density, dt_trigger,
                         mark='o',
                         markstyle='mark size=0.6pt, very thin, semitransparent')
            plot.set_xlabel('Particle density')
            plot.set_ylabel('Difference in trigger time')
            plot.save_as_pdf('scatter')

        plot = Plot()
        c, bins = histogram(dt_trigger, arange(-10, 200, 2.5))
        c = where(c < 100, c, 100)
        plot.histogram(c, bins)
        plot.set_ylimits(0, 100)
        plot.set_ylabel('Counts')
        plot.set_xlabel('Difference in trigger time')
        plot.save_as_pdf('histogram')

        plot = Plot()
        c, bins = histogram(trig_proc, arange(-10, 200, 2.5))
        plot.histogram(c, bins)
        c, bins = histogram(trig_filt, arange(-10, 200, 2.5))
        plot.histogram(c, bins, linestyle='red')
        plot.set_ylimits(0)
        plot.set_ylabel('Counts')
        plot.set_xlabel('Trigger time')
        plot.save_as_pdf('histogram_t')


if __name__ == "__main__":
    # get day of data
    get_data()
    process_data()
    compare_ttrigger()
