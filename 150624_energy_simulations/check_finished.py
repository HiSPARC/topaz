import glob
import os

import tables

from numpy import degrees, log10

if __name__ == "__main__":
    print("Simulations that did not complete:")

    with tables.open_file('/Users/arne/Datastore/CORSIKA/corsika_overview_150624.h5', 'r') as overview:
        for path in glob.glob('*/result.h5'):
            seeds = [int(x) for x in os.path.dirname(path).split('_')]
            simulation = overview.root.simulations.read_where('(seed1 == %d) & (seed2 == %d)' % tuple(seeds))
            with tables.open_file(path, 'r') as data:
                if data.root.coincidences.coincidences.nrows != 100000:
                    print('10**{:.1f} eV, {:.1f} deg'.format(log10(simulation['energy']), degrees(simulation['zenith'])))
                    print('%d_%d' % tuple(seeds), 'N =', data.root.coincidences.coincidences.nrows)
