import tables

from numpy import histogram, linspace

from artist import Plot

STATIONS = [501, 510]
EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def anti_coincidences(data):
    """Analyse events

    Compare density between events in coincidence and those not

    """
    station_groups = ['/s%d' % number for number in STATIONS]
    plot = Plot('semilogy')
    plot2 = Plot()
    ids = [1, 2, 3, 4]

    colors = ['red', 'blue']
    linestyles = ['solid', 'dashed']
    for s_id, s_path in enumerate(data.root.coincidences.s_index):
        events = data.get_node(s_path, 'events')
        # Get all events which are in a coincidence
        ceids = [e_idx
                 for c_idx in data.root.coincidences.c_index
                 for s_idx, e_idx in c_idx if s_idx == s_id]
        coin_events = events.read_coordinates(ceids)
        all_events = events.read()

        bins = linspace(0.01, 40, 300)
        # Should filter -999 values, but there are only ~60 of those.
        coin_counts, bins = histogram(sum(coin_events['n%d' % id] for id in ids) / 2.,
                                      bins=bins)
        all_counts, bins = histogram(sum(all_events['n%d' % id] for id in ids) / 2.,
                                     bins=bins)
        anticoin_counts = all_counts - coin_counts
        # All events
        plot.histogram(all_counts, bins, linestyle='dotted, %s' % colors[s_id])
        # Events in coincidence
        plot.histogram(coin_counts, bins, linestyle='solid, %s' % colors[s_id])
        # Events not in coincidence
        plot.histogram(anticoin_counts, bins, linestyle='dashed, %s' % colors[s_id])

        bins = linspace(0.01, 20, 50)
        coin_counts, bins = histogram(sum(coin_events['n%d' % id] for id in ids) / 2.,
                                      bins=bins)
        all_counts, bins = histogram(sum(all_events['n%d' % id] for id in ids) / 2.,
                                     bins=bins)
        detection_efficiency = coin_counts.astype('float') / all_counts
        plot2.plot((bins[1:] + bins[:-1]) / 2., detection_efficiency,
                   linestyle='%s' % linestyles[s_id], mark=None)

    plot.set_ylimits(min=0.2)
    plot.set_xlimits(min=bins[0], max=15)
    plot.set_ylabel(r'Number of events')
    plot.set_xlabel(r'Particle density [\si{\per\square\meter}]')
    plot.save_as_pdf('anti_coincidences')

    plot2.set_ylimits(min=0., max=1.)
    plot2.set_xlimits(min=0)
    plot2.set_ylabel(r'Chance at coincidence')
    plot2.set_xlabel(r'Particle density [\si{\per\square\meter}]')
    plot2.save_as_pdf('detection_efficiency')


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        anti_coincidences(data)
