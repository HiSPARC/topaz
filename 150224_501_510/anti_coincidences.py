import numpy as np
import tables

from sapphire.clusters import HiSPARCStations

from artist import Plot


STATIONS = [501, 510]
EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def anti_coincidences(data):
    """Analyse events

    Compare density between those in coincidence and those not

    """
    station_groups = ['/s%d' % number for number in STATIONS]
    plot = Plot('semilogy')

    colors = ['red', 'blue']
    for s_idx, s_path in enumerate(data.root.coincidences.s_index):
        events = data.get_node(s_path, 'events')
        ceids = [e[1]
                 for c in data.root.coincidences.c_index
                 for e in c if e[0] == s_idx]
        cevents = events.read_coordinates(ceids)
        aevents = events.read()
        bins = np.linspace(0.01, 40, 300)
        ccounts, bins = np.histogram(cevents['n1'] + cevents['n2'] + cevents['n3'] + cevents['n4'],
                                     bins=bins)
        acounts, bins = np.histogram(aevents['n1'] + aevents['n2'] + aevents['n3'] + aevents['n4'],
                                     bins=bins)
        accounts = acounts - ccounts
        plot.histogram(acounts, bins, linestyle='dotted,%s' % colors[s_idx])
        plot.histogram(ccounts, bins, linestyle='solid,%s' % colors[s_idx])
        plot.histogram(accounts, bins, linestyle='dashed,%s' % colors[s_idx])

    plot.set_ylimits(min=0.2)
    plot.set_xlimits(min=bins[0], max=bins[-1])
    plot.save_as_pdf('anti_coincidences')


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        anti_coincidences(data)
