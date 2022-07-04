import itertools

import tables

from numpy import array, histogram, linspace, nan, where
from scipy.optimize import curve_fit

from artist import Plot

from sapphire.utils import ERR, gauss

COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_141101_150201.h5'
DETECTOR_OFFSETS = {501: [-1.064884, 0.0, 6.217017, 4.851398], 510: [9.416971, 0.0, 9.298256, 8.447724]}


def determine_station_timing_offsets(data):
    """Determine the offsets between the stations."""

    c = 0.3

    ref_station_number = 501
    ref_d_off = DETECTOR_OFFSETS[ref_station_number]
    ref_events = data.root.hisparc.cluster_amsterdam.station_501.events
    ref_t = array(
        [
            where(ref_events.col('t1') == -999, 9000, ref_events.col('t1') - ref_d_off[0]),
            where(ref_events.col('t2') == -999, 9000, ref_events.col('t2') - ref_d_off[1]),
            where(ref_events.col('t3') == -999, 9000, ref_events.col('t3') - ref_d_off[2]),
            where(ref_events.col('t4') == -999, 9000, ref_events.col('t4') - ref_d_off[3]),
        ]
    )
    ref_min_t = ref_t.min(axis=0)

    station_number = 510
    d_off = DETECTOR_OFFSETS[station_number]
    events = data.root.hisparc.cluster_amsterdam.station_510.events
    t = array(
        [
            where(events.col('t1') == -999, 90000, events.col('t1') - d_off[0]),
            where(events.col('t2') == -999, 90000, events.col('t2') - d_off[1]),
            where(events.col('t3') == -999, 90000, events.col('t3') - d_off[2]),
            where(events.col('t4') == -999, 90000, events.col('t4') - d_off[3]),
        ]
    )
    min_t = t.min(axis=0)

    dt = []
    for event, ref_event in zip(events, ref_events):
        if ref_event['t_trigger'] in ERR or event['t_trigger'] in ERR:
            dt.append(nan)
            continue
        dt.append(
            (int(event['ext_timestamp']) - int(ref_event['ext_timestamp']))
            - (event['t_trigger'] - ref_event['t_trigger'])
        )

    dt = array(dt)
    dt = dt + (min_t - ref_min_t)

    plot = Plot()
    bins = linspace(-50, 50, 100)
    y, bins = histogram(dt, bins=bins)
    plot.histogram(y, bins)

    x = (bins[:-1] + bins[1:]) / 2
    try:
        popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0.0, 10))
        station_offset = popt[1]
        plot.draw_vertical_line(station_offset)
        bins = linspace(-50, 50, 1000)
        plot.plot(bins, gauss(bins, *popt), mark=None, linestyle='gray')
    except RuntimeError:
        station_offset = 0.0
    print(station_offset)

    plot.set_title('Time difference, station 510-501')
    plot.set_xlimits(-50, 50)
    plot.set_ylimits(min=0)
    plot.set_xlabel(r'$\Delta t$ [ns]')
    plot.set_ylabel('Counts')
    plot.save_as_pdf('station_offsets')


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'r') as data:
        determine_station_timing_offsets(data)
