""" Overview of Corsika Simulations

Get values from corsika_overview.h5
- particle_id, energy, zenith, azimuth

"""
from random import choice

import tables
import numpy
import artist

from sapphire.corsika.particles import name


OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


# Bins
# t_bins = numpy.arange(-3.75, 56.25, 7.5)
#
# # Particles
# particles = {}
# for p in sims['particle_id']:
#     name = corsika.particles.id[p]
#     if name in particles.keys():
#         particles[name] += 1
#     else:
#         particles[name] = 1
# print particles
#
# pyplot.figure()
# pyplot.xticks(rotation=10)
# pyplot.bar(range(len(particles)), particles.values(), align='center', color='black')
# pyplot.xticks(range(len(particles)), particles.keys())
# pyplot.xlabel('Primary Particle')
# pyplot.ylabel('Count')
# pyplot.title('Number of simulations per primary particle')
# pyplot.show()
#

def plot_energy(energy):
    """Energies"""
    bins = get_unique(energy)
    bins.append(bins[-1] * 10)
    counts, bins = numpy.histogram(energy, bins=bins)
    graph = artist.Plot(axis='semilogx')
    graph.plot(bins[:-1], counts)
    graph.set_xlabel('Energy [eV]')
    graph.set_ylabel('Count')
    graph.set_ylimits(min=0)
    graph.set_title('Number of simulations per primary energy')
    graph.save_as_pdf('energy')


def plot_zenith(zenith):
    """Zeniths"""
    bins = get_unique(zenith)
    bins.append(bins[-1] + bins[-1])
    counts, bins = numpy.histogram(zenith, bins=bins)
    graph = artist.Plot()
    graph.plot(bins[:-1], counts)
    graph.set_xlabel('Zenith [rad]')
    graph.set_ylabel('Count')
    graph.set_ylimits(min=0)
    graph.set_title('Number of simulations per zenith angle')
    graph.save_as_pdf('zenith')


def plot_azimuth(azimuth):
    """Azimuths"""
    bins = get_unique(azimuth)
    bins.append(bins[-1] + bins[-1])
    counts, bins = numpy.histogram(azimuth, bins=bins)
    graph = artist.Plot()
    graph.plot(bins[:-1], counts)
    graph.set_xlabel('Azimuth [rad]')
    graph.set_ylabel('Count')
    graph.set_ylimits(min=0)
    graph.set_title('Number of simulations per azimuth angle')
    graph.save_as_pdf('azimuth')


def plot_energy_zenith(energy, zenith, particle_id=None):
    """Energy, Zenith"""

    e_bins = get_unique(energy)
    e_bins.append(e_bins[-1] + .5)
    z_bins = get_unique(zenith)
    z_bins.append(z_bins[-1] + (z_bins[-1] - z_bins[-2]))
    counts, e_bins, z_bins = numpy.histogram2d(energy, zenith, bins=[e_bins, z_bins])
    graph = artist.Plot() # axis='semilogx'
    graph.histogram2d(numpy.sqrt(counts), e_bins - 0.25, z_bins - (z_bins[1] / 2), type='area')
    graph.set_xlimits(min=10, max=19)
    graph.set_xlabel(r'Energy [\si{electronvolt}]')
    graph.set_ylabel(r'Zenith [\si{\radian}]')
    graph.set_title('Number of simulations per energy and zenith angle')
    if particle_id is None:
        graph.save_as_pdf('energy_zenith')
    else:
        graph.save_as_pdf('energy_zenith_%s' % name(particle_id))


def plot_energy_zenith_per_particle(energy, zenith, particle):
    # Angles vs Energies per Particle
    unique_particles = set(particle)

    for unique_particle in unique_particles:
        s_energy = energy.compress(particle == unique_particle)
        s_zenith = zenith.compress(particle == unique_particle)
        plot_energy_zenith(s_energy, s_zenith, particle_id=unique_particle)


def plot_n_leptons(energy, zenith, particle, n_leptons):
    """Energy, Zenith"""
    color_styles = ('black,', 'red,', 'blue,', 'orange,', 'gray,', 'green,', 'purple,')
    line_styles = ('solid', 'dashed', 'dotted')
    unique_energy = get_unique(energy)
    unique_zenith = get_unique(zenith)
    n_bins = numpy.linspace(0, 8, 300)
    graph = artist.Plot()
    for j, e in enumerate(unique_energy):
        for i, z in enumerate(unique_zenith[::3]):
            n_l = n_leptons.compress((energy == e) & (zenith == z) &
                                     (particle == 14))
            if len(n_l) < 200:
                continue
            counts, n_bins = numpy.histogram(numpy.log10(n_l), bins=n_bins, density=True)
            graph.histogram(counts, n_bins, linestyle=color_styles[j % 5] + line_styles[i % 3])
    graph.set_xlimits(min=0, max=8)
    graph.set_ylimits(min=0)
    graph.set_xlabel('Number of leptons [N]')
    graph.set_ylabel('Count')
    graph.set_title('Distribution of number of leptons per energy and zenith angle')
    graph.save_as_pdf('n_leptons')


def get_data(overview):
    seed1 = overview.root.simulations.col('seed1')
    seed2 = overview.root.simulations.col('seed2')
    seeds = numpy.array(['%d_%d' % (s1, s2) for s1, s2  in zip(seed1, seed2)])
    particle = overview.root.simulations.col('particle_id')
    energy = numpy.log10(overview.root.simulations.col('energy'))
    zenith = overview.root.simulations.col('zenith')
    azimuth = overview.root.simulations.col('azimuth')
    n_leptons = (overview.root.simulations.col('n_electron') +
                 overview.root.simulations.col('n_muon'))
    return seeds, particle, energy, zenith, azimuth, n_leptons


def get_unique(parameter):
    return sorted(list(set(parameter)))


def get_random_seed(seeds, particle, energy, zenith, e, z):
    result = seeds.compress((energy == e) & (zenith == z) & (particle == 14))
    try:
        return choice(result)
    except IndexError:
        return None


def get_seed_matrix(seeds, particle, energy, zenith):
    """Get random seed for each combination of Zenith and Energy.

    :param seeds,particle,energy,zenith: columns from simulations table.

    """
    unique_energy = get_unique(energy)
    unique_zenith = get_unique(zenith)

    for en in unique_energy:
        for zen in unique_zenith:
            seed = get_random_seed(seeds, particle, energy, zenith, en, zen)
            print ('Energy: 10^%d, Zenith: %4.1f: %s' %
                   (en, numpy.degrees(zen), seed))


if __name__ == '__main__':
    with tables.open_file(OVERVIEW, 'r') as overview:
        seeds, particle, energy, zenith, azimuth, n_leptons = get_data(overview)
    plot_n_leptons(energy, zenith, particle, n_leptons)
    plot_energy_zenith(energy, zenith, particle_id=14)
#     plot_energy(energy)
#     plot_zenith(zenith)
#     plot_azimuth(azimuth)
#     plot_energy_zenith_per_particle(energy, zenith, particle)
#     get_seed_matrix(seeds, particle, energy, zenith)
