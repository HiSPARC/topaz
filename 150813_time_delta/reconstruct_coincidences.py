from datetime import datetime

import tables
from numpy import (genfromtxt, histogram, linspace, pi, where, degrees, arange,
                   invert, array, percentile, isfinite)

from artist import Plot

from sapphire import (download_data, ReconstructESDEvents, CoincidencesESD,
                      CoincidenceQuery, HiSPARCStations)
from sapphire.transformations.clock import gps_to_datetime
from sapphire.utils import angle_between

STATIONS = [501, 510]
DATA = 'data_coin.h5'


def download_dataset():
    print 'Downloading data . . .'
    with tables.open_file(DATA, 'w'):
        # Clear previous data
        pass
    for station in STATIONS:
        delta_data = genfromtxt('data/time_delta_%d.csv' % station, delimiter='\t', dtype=None,
                                names=['ext_timestamp', 'time_delta'])
        start = gps_to_datetime(delta_data['ext_timestamp'][0] / int(1e9))
        end = gps_to_datetime(delta_data['ext_timestamp'][-1] / int(1e9))

        with tables.open_file(DATA, 'a') as data:
            download_data(data, '/s%d' % station, station, start, end)
            download_data(data, '/s%d_original' % station, station, start, end)

        with tables.open_file(DATA, 'a') as data:
            events = data.get_node('/s%d' % station, 'events')

            # Data ends before delta list because I got delta data from today
            delta_ets_list = delta_data['ext_timestamp'].tolist()
            stop_idx = delta_ets_list.index(events[-1]['ext_timestamp']) + 1
            time_delta = delta_data['time_delta'][:stop_idx]

            event_ets_list = events.col('ext_timestamp').tolist()
            idx = event_ets_list.index(delta_ets_list[0])
            events.remove_rows(0, idx)
            try:
                last_idx = event_ets_list[idx::].index(delta_ets_list[-1]) - idx
            except ValueError:
                pass
            else:
                events.remove_rows(last_idx)
            events.flush()

            assert all(events.col('ext_timestamp') == delta_data['ext_timestamp'])
            t3 = events.col('t3')
            t4 = events.col('t4')
            events.modify_column(colname='t3',
                                 column=where(t3 >= 0, t3 + time_delta, t3))
            events.modify_column(colname='t4',
                                 column=where(t4 >= 0, t4 + time_delta, t4))
            events.flush()


def find_coincidences():
    print 'Coincidences . . .'
    with tables.open_file(DATA, 'a') as data:
        cluster = HiSPARCStations(STATIONS)
        coin = CoincidencesESD(data, '/coincidences', ['/s%d' % s for s in STATIONS])
        coin.search_and_store_coincidences(cluster=cluster)
        coin = CoincidencesESD(data, '/coincidences_original', ['/s%d_original' % s for s in STATIONS])
        coin.search_and_store_coincidences(cluster=cluster)
        coin = CoincidencesESD(data, '/coincidences_501_original', ['/s501_original', '/s510'])
        coin.search_and_store_coincidences(cluster=cluster)
        coin = CoincidencesESD(data, '/coincidences_510_original', ['/s501', '/s510_original'])
        coin.search_and_store_coincidences(cluster=cluster)


def reconstruct_events():
    print 'Reconstructions . . .'
    with tables.open_file(DATA, 'a') as data:
        for station in STATIONS:
            rec = ReconstructESDEvents(data, '/s%d_original' % station, station, overwrite=True)
            rec.reconstruct_and_store()
            reco = ReconstructESDEvents(data, '/s%d' % station, station, overwrite=True)
            reco.reconstruct_and_store()


def plot_reconstructions():
    print 'Plotting . . .'
    plot = Plot()
    bins = linspace(0, 90, 30)  # Degrees
    plot.set_ylimits(min=0)
    plot.set_xlimits(0, 90)
    plot.set_ylabel('counts')
    plot.set_xlabel(r'Angle between [\si{\degree}]')
    colors = ['black', 'red', 'green', 'blue']

    for i, c_group in enumerate(['/coincidences', '/coincidences_original',
                                 '/coincidences_501_original', '/coincidences_510_original']):
        cq = CoincidenceQuery(DATA, coincidence_group=c_group)
        coincidences = cq.all([501, 510], iterator=True)
        reconstructions = [cq._get_reconstructions(c) for c in coincidences]
        cq.finish()

        azi501 = []
        zen501 = []
        azi510 = []
        zen510 = []

        for rec1, rec2 in reconstructions:
            if rec1[0] == 501:
                azi501.append(rec1[1]['azimuth'])
                zen501.append(rec1[1]['zenith'])
                azi510.append(rec2[1]['azimuth'])
                zen510.append(rec2[1]['zenith'])
            else:
                azi501.append(rec2[1]['azimuth'])
                zen501.append(rec2[1]['zenith'])
                azi510.append(rec1[1]['azimuth'])
                zen510.append(rec1[1]['zenith'])

        azi501 = array(azi501)
        zen501 = array(zen501)
        azi510 = array(azi510)
        zen510 = array(zen510)

        # Compare angles between old and new
        d_angle = angle_between(zen501, azi501, zen510, azi510)
        print c_group, r'67\%% within %.1f degrees' % degrees(percentile(d_angle[isfinite(d_angle)], 67))
        plot.histogram(*histogram(degrees(d_angle), bins=bins), linestyle=colors[i])
    plot.save_as_pdf('angle_between_501_510')



def print_coincident_time_delta():

    cq = CoincidenceQuery(DATA, coincidence_group='/coincidences')
    coincidences = cq.coincidences
    events = [cq._get_events(c) for c in coincidences]

    cq_orig = CoincidenceQuery(DATA, coincidence_group='/coincidences_original')
    coincidences_orig = cq_orig.coincidences
    events_orig = [cq_orig._get_events(c) for c in coincidences_orig]

    t3_501 = []
    t3_510 = []

    for event1, event2 in events:
        if event1[0] == 501:
            t3_501.append(event1[1]['t3'])
            t3_510.append(event2[1]['t3'])
        else:
            t3_501.append(event2[1]['t3'])
            t3_510.append(event1[1]['t3'])

    t3_501_orig = []
    t3_510_orig = []

    for event1, event2 in events_orig:
        if event1[0] == 501:
            t3_501_orig.append(event1[1]['t3'])
            t3_510_orig.append(event2[1]['t3'])
        else:
            t3_501_orig.append(event2[1]['t3'])
            t3_510_orig.append(event1[1]['t3'])

    t3_501 = array(t3_501)
    t3_510 = array(t3_510)
    t3_501_orig = array(t3_501_orig)
    t3_510_orig = array(t3_510_orig)

    filter = (t3_501_orig != -999) & (t3_510_orig != -999)

    dt3_501 = t3_501 - t3_501_orig
    dt3_510 = t3_510 - t3_510_orig
    dt = dt3_501 - dt3_510

    # Plot distribution
    plot = Plot()
    counts, bins = histogram(dt.compress(filter), bins=arange(-10.5, 11.5, 1))
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_ylabel('counts')
    plot.set_xlabel(r'time delta [\si{\nano\second}]')
    plot.save_as_pdf('time_delta_501_510')



def print_offsets():
    with tables.open_file(DATA, 'r') as data:
        print '501'
        print data.root.s501.detector_offsets[:]
        print 'without time_delta'
        print data.root.s501_original.detector_offsets[:]
        print '510'
        print data.root.s510.detector_offsets[:]
        print 'without time_delta'
        print data.root.s510_original.detector_offsets[:]


if __name__ == "__main__":
    download_dataset()
    find_coincidences()
    reconstruct_events()
    print_coincident_time_delta()
    plot_reconstructions()
    print_offsets()
