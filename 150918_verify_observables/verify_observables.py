""" Try to do an offline reconstruction of the trace variables.

The new DAQ (v4) uses a lower threshold for the integral and baseline.
This needs to be selected if these traces are reconstructed.

If the mean filter is enabled the reconstruction does not work because
the DAQ used the raw traces for the reconstruction.

If data reduction is enabled on the old DAQ to much of the traces
are cut away, preventing reconstruction of the baselines.
Additionally small pulsheights in channels without big signals (below
baseline_threshold) may be cut away, preventing their reconstruction
However, due to the tiny pulses these are uninteressting anyway.

"""
from datetime import datetime

import tables
from numpy.testing import assert_allclose

from sapphire.publicdb import download_data
from sapphire.analysis import process_traces
from sapphire import ProcessEvents

# 501 - HiSPARC III new DAQ disabled filter no data reduction
# 510 - HiSPARC III old DAQ disabled filter with data reduction
# 202 - HiSPARC II PySPARC no filter no data reduction
# 304 - HiSPARC II old DAQ with filter and data reduction
STATIONS = [501, 510, 202, 304]
DATA_PATH = '/Users/arne/Datastore/verify/data.h5'


def download():
    start = datetime(2015, 9, 16)
    end = datetime(2015, 9, 16, 0, 10)
    with tables.open_file(DATA_PATH, 'w') as data:
        for station in STATIONS:
            download_data(data, '/s%d' % station, station, start, end,
                          get_blobs=True)


def reconstruct_observables():
    with tables.open_file(DATA_PATH, 'r') as data:
        default_threshold = process_traces.BASELINE_THRESHOLD
        default_low_iii = process_traces.LOW_THRESHOLD_III
        default_low_ii = process_traces.LOW_THRESHOLD

        for station in STATIONS:
            if station in [202, 510, 304]:
                process_traces.BASELINE_THRESHOLD = 25
            else:
                process_traces.BASELINE_THRESHOLD = default_threshold
            if station in [501]:
                process_traces.LOW_THRESHOLD_III = 56
            else:
                process_traces.LOW_THRESHOLD_III = default_low_iii
            if station in [510]:
                process_traces.LOW_THRESHOLD = 226
            else:
                process_traces.LOW_THRESHOLD = default_low_ii

            pe = ProcessEvents(data, '/s%d' % station)
            wrong = {'baseline': 0, 'std_dev': 0, 'n_peaks': 0,
                     'pulseheights': 0, 'integrals': 0}
            for event in pe.source:
                traces = pe.get_traces_for_event(event)
                to = process_traces.TraceObservables(traces)

                try:
                    assert_allclose(to.baselines, event['baseline'], atol=0)
                except AssertionError:
                    try:
                        assert_allclose(to.baselines, event['baseline'], atol=1)
                    except AssertionError:
                        wrong['baseline'] += 1
                    # print 'baseline:', event['event_id'], to.baselines, event['baseline']
                    to.baselines = event['baseline']
                assert_allclose(to.baselines, event['baseline'], atol=0)

                try:
                    assert_allclose(to.std_dev, event['std_dev'], atol=0)
                except AssertionError:
                    wrong['std_dev'] += 1
#                     print 'std_dev:', event['event_id'], to.std_dev, event['std_dev']
                try:
                    assert_allclose(to.n_peaks, event['n_peaks'], atol=0)
                except AssertionError:
                    wrong['n_peaks'] += 1
#                     print 'n_peaks:', event['event_id'], to.n_peaks, event['n_peaks']
                try:
                    assert_allclose(to.pulseheights, event['pulseheights'], atol=0)
                except AssertionError:
                    wrong['pulseheights'] += 1
#                     print 'pulseheights:', event['event_id'], to.pulseheights, event['pulseheights']
                try:
                    assert_allclose(to.integrals, event['integrals'], atol=0)
                except AssertionError:
                    wrong['integrals'] += 1
#                     print 'integrals:', event['event_id'], to.integrals, event['integrals']
            print 'station:', station, wrong, 'total:', pe.source.nrows

if __name__ == "__main__":
    # download()
    reconstruct_observables()
