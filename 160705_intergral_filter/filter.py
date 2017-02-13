import os
import zlib

import tables
import datetime
from numpy import array, histogram2d, histogram, linspace

from artist import Plot, MultiPlot

from sapphire import Station
from sapphire.publicdb import download_data
from sapphire.analysis.process_traces import TraceObservables, MeanFilter
from sapphire.utils import pbar


DATA_PATH = '/Users/arne/Datastore/intergral_filter/data.h5'
STATION = 505
GROUP = '/s%d' % STATION
API_STATION = Station(STATION)
COLORS = ['black', 'red', 'green', 'blue']


def get_data():
    """Ensure data is downloaded and available"""

    if not os.path.exists(DATA_PATH):
        with tables.open_file(DATA_PATH, 'w') as data:
            start = datetime.datetime(2014, 6, 10)
            end = datetime.datetime(2014, 6, 11)
            download_data(data, GROUP, STATION, start, end, get_blobs=True)


def get_traces_from_api(station, event):
    return retrieve_traces(station, event['timestamp'], event['nanoseconds'])


def retrieve_traces(station, ts, ns):
    """Get trace using API"""

    return array(station.event_trace(ts, ns, raw=True)).T


def get_traces_from_blobs(event, blobs):
    traces = [unpack_trace(blobs[idx]) if idx >= 0 else []
              for idx in event['traces']]

    return array(traces).T


def unpack_trace(blob_trace):
    try:
        trace = zlib.decompress(blob_trace).split(',')
    except zlib.error:
        trace = zlib.decompress(blob_trace[1:-1]).split(',')
    if trace[-1] == '':
        del trace[-1]
    trace = [int(x) for x in trace]
    return trace


def determine_integrals(traces, event):
    observables = TraceObservables(traces)
    observables.baselines = event['baseline']
    raw_integral = observables.integrals

    filtered_traces = array(MeanFilter().filter_traces(traces.T)).T
    observables = TraceObservables(filtered_traces)
    observables.baselines = event['baseline']
    filtered_integral = observables.integrals
    return raw_integral, filtered_integral


def get_integrals(data):
    blobs = data.get_node(GROUP, 'blobs')
    events = data.get_node(GROUP, 'events')

    raw_integrals = []
    filtered_integrals = []
    source_integrals = []

    for event in pbar(events[:2000]):
        # traces = get_traces_from_api(API_STATION, event)
        traces = get_traces_from_blobs(event, blobs)
        raw, filtered = determine_integrals(traces, event)
        source = event['integrals']
        raw_integrals.append(raw)
        filtered_integrals.append(filtered)
        source_integrals.append(source)
    return (array(raw_integrals), array(filtered_integrals),
            array(source_integrals))


def compare_integrals(before, after):
    if len(before) > 5000:
        plot = MultiPlot(4, 1, width=r'.6\textwidth', height=r'.3\textwidth')
        bins = [linspace(100, 6000, 20), linspace(-150, 150, 20)]
        for i, splot in enumerate(plot.subplots):
            c, x, y = histogram2d(before[:, i], after[:, i] - before[:, i], bins=bins)
#             splot.histogram2d(c, x, y, bitmap=True, type='color', colormap='viridis')
            splot.histogram2d(c, x, y, type='area')
        plot.show_yticklabels_for_all(None)
        plot.show_xticklabels(3, 0)
        plot.save_as_pdf('hist2d')
    else:
        plot = MultiPlot(4, 1, 'semilogx', width=r'.6\textwidth', height=r'.3\textwidth')
        for i, splot in enumerate(plot.subplots):
            splot.scatter(before[:, i], after[:, i] - before[:, i],
                          mark='o',
                          markstyle='mark size=0.6pt, very thin, '
                                    'semitransparent, %s' % COLORS[i])
        plot.show_yticklabels_for_all(None)
        plot.show_xticklabels(3, 0)
        plot.set_xlimits_for_all(None, 100, 100000)
        plot.set_ylimits_for_all(None, -150, 150)
        plot.save_as_pdf('scatter')

    plot = MultiPlot(4, 1, width=r'.6\textwidth', height=r'.3\textwidth')
    for i, splot in enumerate(plot.subplots):
        filter = before[:, i] > 0  # Ignore detectors/events with no signal
        c, bins = histogram(after[:, i][filter] - before[:, i][filter], linspace(-150, 150, 100))
        splot.histogram(c, bins, linestyle='%s' % COLORS[i])
    plot.show_yticklabels_for_all(None)
    plot.show_xticklabels(3, 0)
    plot.set_xlimits_for_all(None, -150, 150)
    plot.set_ylimits_for_all(None, 0)
    plot.save_as_pdf('histogram')


if __name__ == "__main__":
    # get day of data
    get_data()
    if 'raw' not in globals():
        with tables.open_file(DATA_PATH, 'r') as data:
            raw, filtered, source = get_integrals(data)
    compare_integrals(raw, filtered)
