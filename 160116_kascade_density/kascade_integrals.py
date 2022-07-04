"""Find events belonging to the reconstructed data

HiSPARC and KASCADE data were combined, but only included pulseheight
(n#) data. The pulseintegral might be a better measure for particle density.
Attempt to find the events that belong to the reconstruced data.

Note: I normalized the event_ids in the events table. The event_ids were
1-based, and were modified to be 0-based. The following code was used:

    events.modify_column(column=range(events.nrows), colname='event_id')

"""
import tables

from sapphire.utils import pbar

DATA_PATH = '/Users/arne/Datastore/kascade/kascade-20080912.h5'


if __name__ == "__main__":
    ids = [1, 2, 3, 4]
    with tables.open_file(DATA_PATH, 'r') as data:
        event_ids = []
        recs = data.root.reconstructions.iterrows()
        events = data.root.hisparc.cluster_kascade.station_601.events.iterrows()
        for rec in pbar(recs, length=data.root.reconstructions.nrows):
            for event in events:
                if all(rec['n%d' % id] == event['n%d' % id] for id in ids):
                    event_ids.append(event['event_id'])
                    break
    with tables.open_file(DATA_PATH, 'a') as data:
        data.create_array('/', 'c_index', event_ids)
        events = data.root.hisparc.cluster_kascade.station_601.events
        integrals = events.read_coordinates(event_ids, 'integrals')
        data.create_array('/', 'reconstructions_integrals', integrals)
        data.create_array('/', 'reconstructions_integrals_n', integrals / 5000.0)
