""" Reconstruct the results

"""
import glob
import os

import tables

from sapphire import ReconstructESDCoincidences

RESULT_PATH = '/Users/arne/Datastore/science_park_corsika/{seed}/result.h5'
PATHS = '/Users/arne/Datastore/science_park_corsika/*_*/result.h5'


def reconstruct_simulations(seed):
    path = RESULT_PATH.format(seed=seed)
    with tables.open_file(path, 'a') as data:
        cluster = data.root.coincidences._v_attrs.cluster

        rec_coins = ReconstructESDCoincidences(data, '/coincidences',
                                               overwrite=True, progress=True,
                                               cluster=cluster)
        rec_coins.prepare_output()
        rec_coins.offsets = {station.number: [d.offset + station.gps_offset
                                              for d in station.detectors]
                             for station in cluster.stations}
        rec_coins.reconstruct_directions()
        rec_coins.reconstruct_cores()
        rec_coins.store_reconstructions()


if __name__ == '__main__':
    for path in glob.glob(PATHS):
        seed = os.path.basename(os.path.dirname(path))
        print(seed)
        reconstruct_simulations(seed)
