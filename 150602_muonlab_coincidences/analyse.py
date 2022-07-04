import numpy as np
import tables

from artist import Plot

from sapphire import CoincidenceQuery

EVENTDATA_PATHS = ['/Users/arne/Datastore/muonlab_test.h5',
                   '/Users/arne/Datastore/muonlab_test2.h5',
                   '/Users/arne/Datastore/muonlab_test3.h5']


def analyse(data, id):
    event_node = data.get_node('/station_99/events')
    print('Total number of events: %d' % event_node.nrows)
    cq = CoincidenceQuery(data)
    coincidences = cq.all(stations=[99])
    coincident_events = cq.events_from_stations(coincidences, [99], n=1)
    coincident_event_ids = [e[0][1]['event_id'] for e in coincident_events]
    event_ids = [i for i in range(event_node.nrows)
                 if i not in coincident_event_ids]
    events = event_node.read_coordinates(event_ids)
    coincident_events = event_node.read_coordinates(coincident_event_ids)
    print('Total number of events not in coincidence: %d' % len(events))
    print('Total number of events in coincidence: %d' % len(coincident_events))

    cph1 = coincident_events['pulseheights'][:, 0]
    cph2 = coincident_events['pulseheights'][:, 1]
    ph1 = events['pulseheights'][:, 0]
    ph2 = events['pulseheights'][:, 1]
    plot = Plot()
    bins = np.arange(0, 4000, 50)
    for ph, ls in [(cph1, 'black,dotted'), (cph2, 'red,dotted'),
                   (ph1, 'black'), (ph2, 'red')]:
        counts, bins = np.histogram(ph, bins=bins)
        plot.histogram(counts, bins, linestyle=ls)
    plot.set_xlimits(min=0, max=4000)
    plot.set_ylimits(min=.5)
    plot.set_ylabel('Counts')
    plot.set_xlabel('Pulseheight [ADC]')
    plot.save_as_pdf('muonlab_pulseheights_%d' % id)

    cdt = coincident_events['t2'] - coincident_events['t1']
    dt = events['t2'] - events['t1']
    plot = Plot()
    bins = np.arange(-100, 100, 2.5)
    for t, ls in [(dt, ''), (cdt, 'dotted')]:
        counts, bins = np.histogram(t, bins=bins)
        plot.histogram(counts, bins, linestyle=ls)
    plot.set_ylimits(min=0)
    plot.set_ylabel('Counts')
    plot.set_xlabel('Time difference [ns]')
    plot.save_as_pdf('muonlab_dt_%d' % id)


if __name__ == '__main__':
    for id, data_path in enumerate(EVENTDATA_PATHS):
        with tables.open_file(data_path, 'r') as data:
            analyse(data, id)
