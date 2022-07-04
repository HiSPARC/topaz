import numpy
import tables

from matplotlib import pyplot

from sapphire.corsika.particles import name

OVERVIEW_PATH = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def add_rightmost_bin(bins):
    new_bins = bins[:]
    new_bins.append(bins[-1] + (bins[-1] - bins[-2]))
    return new_bins


def print_overview(sims):
    particles = sorted(set(sims.col('particle_id')))
    energies = sorted(set(sims.col('energy')))
    zeniths = sorted(set(sims.col('zenith')))

    e_bins = add_rightmost_bin(energies)
    z_bins = add_rightmost_bin(zeniths)

    prows = {particle: sims.read_where('particle_id==particle')
             for particle in particles}
    for particle, rows in prows.items():
        print('Particle: %s (%d)' % (name(particle), particle))
        histogram = numpy.histogram2d(rows['energy'], rows['zenith'],
                                      bins=[e_bins, z_bins])
        print('Zenith >' + '% 6g° |' * len(zeniths) % tuple(numpy.degrees(zeniths)))
        print('Energy v' + '---------' * len(zeniths))
        for energy, counts in zip(energies, histogram[0]):
            print('% 7.1f:' % numpy.log10(energy) + '% 7d |' * len(counts) % tuple(counts))


def plot_number_of_particles(sims):
    energies = sorted(set(sims.col('energy')))
    zeniths = sorted(set(sims.col('zenith')))

    fig, (ax1, ax2) = pyplot.subplots(1, 2, sharey=False, sharex=False)
    ne_bins = numpy.logspace(0, 9, 200)

    # protons
    filtered_rows = sims.read_where('(particle_id==14)')

    energy = energies[3]
    for zenith in zeniths:
        rows = [row for row in filtered_rows
                if row['energy'] == energy and row['zenith'] == zenith]
        if len(rows) > 10:
            weights = numpy.ones(len(rows)) / float(len(rows))
            ax1.hist([r['n_electron'] for r in rows], bins=ne_bins,
                     histtype='step', weights=weights,
                     label='{:4.1f} deg, {:.g} eV'.format(numpy.degrees(zenith), energy))
    ax1.set_xscale('log')
    ax1.set_xlabel('Number of electrons')
    ax1.legend(loc=2)

    zenith = zeniths[3]
    for energy in energies:
        rows = [row for row in filtered_rows
                if row['energy'] == energy and row['zenith'] == zenith]
        if len(rows) > 10:
            weights = numpy.ones(len(rows)) / float(len(rows))
            ax2.hist([r['n_muon'] for r in rows], bins=ne_bins,
                     histtype='step', weights=weights,
                     label='{:4.1f} deg, {:.g} eV'.format(numpy.degrees(zenith), energy))
    ax2.set_xscale('log')
    ax2.set_xlabel('Number of electrons')
    ax2.legend(loc=2)
    fig.show()


def main():
    with tables.open_file(OVERVIEW_PATH, 'r') as data:
        sims = data.get_node('/simulations')
        print_overview(sims)
        plot_number_of_particles(sims)


if __name__ == '__main__':
    main()
