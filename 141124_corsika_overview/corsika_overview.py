""" Overview of Corsika Simulations

Get values from corsika_overview.h5
- particle_id, energy, zenith, azimuth

"""
from itertools import cycle
from random import choice

import numpy
import tables

import artist

from sapphire import CorsikaQuery
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
    graph.set_xlabel(r'Azimuth [\si{\radian}]')
    graph.set_ylabel('Count')
    graph.set_ylimits(min=0)
    graph.set_title('Number of simulations per azimuth angle')
    graph.save_as_pdf('azimuth')


def plot_energy_zenith(cq, particle=None):
    """Energy, Zenith"""

    e_bins = numpy.arange(11, 18.6, 0.5) - 0.25
#     e_bins = sorted(cq.available_parameters('energy', particle=particle))
#     e_bins.append(e_bins[-1] + 0.5)
    z_bins = numpy.arange(0, 67.6, 7.5) - 3.75
#     z_bins = sorted(cq.available_parameters('zenith', particle=particle))
#     z_bins.append(z_bins[-1] + 7.5)

    simulations = cq.simulations(particle=particle)
    energy = numpy.log10(simulations['energy'])
    zenith = numpy.degrees(simulations['zenith'])

    counts, e_bins, z_bins = numpy.histogram2d(energy, zenith,
                                               bins=[e_bins, z_bins])
    graph = artist.Plot()  # axis='semilogx'
    graph.histogram2d(numpy.sqrt(counts), e_bins, z_bins,
                      type='area')
    graph.set_xlimits(min=10, max=19)
    graph.set_xlabel(r'Energy [Log10 \si{\eV}]')
    graph.set_ylabel(r'Zenith [\si{\degree}]')
    graph.set_title('Number of simulations per energy and zenith angle')
    if particle is not None:
        graph.save_as_pdf('energy_zenith_%s' % particle)
    else:
        graph.save_as_pdf('energy_zenith')


def plot_energy_zenith_per_particle(cq):
    """Energy v zenith per primary particle"""

    for particle in cq.all_particles:
        plot_energy_zenith(cq, particle=particle)


def plot_n_leptons(cq):
    """Energy, Zenith"""

    color_styles = cycle(('black,', 'red,', 'blue,', 'orange,', 'gray,',
                          'green,',))

    n_bins = numpy.linspace(0, 8, 300)
    graph = artist.Plot()
    energies = sorted(cq.available_parameters('energy'))
    for e, c in zip(energies, color_styles):
        zeniths = sorted(cq.available_parameters('zenith', energy=e))
        line_styles = cycle(('solid', 'dashed', 'dotted', 'densely dashed'))
        for z, l in zip(zeniths[::3], line_styles):
            sims = cq.simulations(energy=e, zenith=z)
            n_leptons = sims['n_muon'] + sims['n_electron']
            if len(n_leptons) < 200:
                continue
            counts, n_bins = numpy.histogram(numpy.log10(n_leptons),
                                             bins=n_bins, density=True)
            graph.histogram(counts, n_bins,
                            linestyle=c + l)
    graph.set_xlimits(min=0, max=9)
    graph.set_ylimits(min=0)
    graph.set_xlabel('Number of leptons [N]')
    graph.set_ylabel('Count')
#     graph.set_title('Distribution of number of leptons per energy and '
#                     'zenith angle')
    graph.save_as_pdf('n_leptons')


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
        cq = CorsikaQuery(overview)
        plot_n_leptons(cq)
        plot_energy_zenith(cq)
        plot_energy_zenith_per_particle(cq)

#     plot_azimuth(azimuth)
#     get_seed_matrix(seeds, particle, energy, zenith)
