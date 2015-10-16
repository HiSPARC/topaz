from __future__ import division

import glob

from numpy import isnan, degrees, log10, array, sqrt
import tables

from sapphire.utils import pbar


#PATHS = '/Users/arne/Datastore/cluster_efficiency/151013*.h5'
PATHS = '/Users/arne/Datastore/cluster_efficiency/151014_*.h5'


def get_combined_results():
    zenith = []
    zenith_in = []
    energy_in = []
    size_in = []
    r_in = []

    zenith_init = []
    energy_init = []
    size_init = []
    r_init = []

    for path in pbar(glob.glob(PATHS)):
        with tables.open_file(path, 'r') as data:
            recs = data.root.coincidences.reconstructions
            filtered_recs = recs.read_where('s501 & s502 & s503 & s504 & s505 & s506')
            zenith.extend(degrees(filtered_recs['zenith']))
            zenith_in.extend(degrees(filtered_recs['reference_zenith']))
            energy_in.extend(log10(filtered_recs['reference_energy']))
            size_in.extend(log10(filtered_recs['reference_size']))
            r_in.extend(sqrt(filtered_recs['reference_x']**2 + filtered_recs['reference_y']**2))

            zenith_init.extend(degrees(recs.col('reference_zenith')))
            energy_init.extend(log10(recs.col('reference_energy')))
            size_init.extend(log10(recs.col('reference_size')))
            r_init.extend(sqrt(recs.col('reference_x')**2 + recs.col('reference_y')**2))

    zenith = array(zenith)
    filter = ~isnan(zenith)

    zenith = zenith.compress(filter)
    zenith_in = array(zenith_in).compress(filter)
    energy_in = array(energy_in).compress(filter)
    size_in = array(size_in).compress(filter)
    r_in = array(r_in).compress(filter)

    zenith_init = array(zenith_init)
    energy_init = array(energy_init)
    size_init = array(size_init)
    r_init = array(r_init)


    return (zenith, zenith_in, energy_in, size_in, r_in,
            zenith_init, energy_init, size_init, r_init)


def plots():
    for e in [16, 16.5, 17, 17.5]:
        figure()
        title('Input and detected zeniths for shower energy: %.1f' % e)

        c_init, b = histogram(zenith_init.compress(energy_init == e), bins=arange(-3.75, 63.76, 7.5))
        c_in, b = histogram(zenith_in.compress(energy_in == e), bins=arange(-3.75, 63.76, 7.5))
        plot((b[1:] + b[:-1]) / 2, where(isnan(c_in/c_init), 0, sin(radians(b[1:])) * c_in / c_init))

        print 'Energy:', e
        print (b[1:] + b[:-1]) / 2
        print c_in
        print c_init

    figure()
    for e in [16, 16.5, 17, 17.5]:
        title('Reconstructed zeniths per shower energy')
        hist(zenith.compress(energy_in == e), bins=arange(0, 60, 1), alpha=.5)

    figure()
    title('Detected core distances vs shower energy')
    hist2d(r_in, energy_in, bins=(arange(0, 600, 40), arange(15.75, 17.76, .5)), cmap='coolwarm')

    figure()
    title('Detected core distances vs shower energy, scaled to bin area')
    counts, xbins, ybins = histogram2d(r_in, energy_in, bins=(arange(0, 600, 40), arange(15.75, 17.76, .5)))
    imshow(-counts.T/(pi * (xbins[:-1]**2 - xbins[1:] **2)), interpolation='nearest', cmap='coolwarm', extent=(0, 560, 1575, 1775))
    print counts.T/(pi * (xbins[:-1]**2 - xbins[1:] **2)


if __name__ == "__main__":
    zenith, zenith_in, energy_in, size_in, r_in, zenith_init, energy_init, \
        size_init, r_init = get_combined_results()
