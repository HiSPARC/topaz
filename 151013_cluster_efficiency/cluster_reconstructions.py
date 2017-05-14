from __future__ import division

import glob

import tables

from sapphire import ReconstructESDCoincidences, ReconstructESDEvents
from sapphire.utils import pbar

#PATHS = '/Users/arne/Datastore/cluster_efficiency/151013*.h5'
PATHS = '/Users/arne/Datastore/cluster_efficiency/151014_1*.h5'


def reconstruct_simulations(path):
    with tables.open_file(path, 'a') as data:
        cluster = data.root.coincidences._v_attrs.cluster

        # Reconstruct each station
        for station in cluster.stations:
            station_group = '/cluster_simulations/station_%d' % station.number
            rec_events = ReconstructESDEvents(data, station_group, station,
                                              overwrite=True, progress=False)
            rec_events.prepare_output()
            rec_events.offsets = [d.offset for d in station.detectors]
            rec_events.store_offsets()
            rec_events.reconstruct_directions()
            rec_events.store_reconstructions()

        # Reconstruct coincidences
        rec_coins = ReconstructESDCoincidences(data, '/coincidences',
                                               overwrite=True, progress=False)
        rec_coins.prepare_output()
        rec_coins.offsets = {station.number: [d.offset + station.gps_offset
                                              for d in station.detectors]
                             for station in cluster.stations}
        rec_coins.reconstruct_directions()
        rec_coins.store_reconstructions()


if __name__ == "__main__":
    for path in pbar(glob.glob(PATHS)):
        reconstruct_simulations(path)
