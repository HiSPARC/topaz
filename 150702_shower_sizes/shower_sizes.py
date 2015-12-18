from artist import Plot
import tables
from numpy import (log10, median, percentile, degrees, array, arange,
                   histogram, logspace, mean)

from sapphire import CorsikaQuery

# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def plot_shower_size(leptons=['electron', 'muon']):
    plot = Plot(axis='semilogy')
    cq = CorsikaQuery(OVERVIEW)
    p = 'proton'
    for e in sorted(cq.available_parameters('energy', particle=p)):
        median_size = []
        min_size = []
        max_size = []
        zeniths = sorted(cq.available_parameters('zenith', energy=e, particle=p))
        for z in zeniths:
            selection = cq.simulations(zenith=z, energy=e, particle=p)
            n_leptons = selection['n_%s' % leptons[0]]
            for lepton in leptons[1:]:
                n_leptons += selection['n_%s' % lepton]
            median_size.append(median(n_leptons))
            min_size.append(percentile(n_leptons, 16))
            max_size.append(percentile(n_leptons, 84))
        if len(zeniths):
            plot.plot(zeniths, median_size, linestyle='very thin')
            plot.shade_region(zeniths, min_size, max_size, color='lightgray,semitransparent')
            plot.add_pin('%.1f' % e, relative_position=0)
    plot.set_xticks([t for t in arange(0, 60.1, 7.5)])
    plot.set_ylimits(1, 1e9)
    plot.set_ylabel(r'Shower size (leptons)')
    plot.set_xlabel(r'Zenith [\si{\degree}]')
    plot.save_as_pdf('shower_sizes_%s' % '_'.join(leptons))
    cq.finish()

def plot_shower_size_distributions():
    plot = Plot(axis='semilogx')
    cq = CorsikaQuery(OVERVIEW)
    p = 'proton'
    z = 0
    for e in sorted(cq.available_parameters('energy', particle=p, zenith=z)):
        selection = cq.simulations(zenith=z, energy=e, particle=p)
        n_leptons = selection['n_muon'] + selection['n_electron']
        plot.histogram(*histogram(n_leptons, bins=logspace(0, 9, 200)))
        plot.add_pin('%.1f' % e, x=mean(n_leptons), location='above')
    plot.set_ylimits(min=0)
    plot.set_xlimits(1, 1e9)
    plot.set_ylabel(r'pdf')
    plot.set_xlabel(r'Shower size (leptons)')
    plot.save_as_pdf('shower_size_distribution')
    cq.finish()


if __name__ == "__main__":
#     plot_shower_size()
#     plot_shower_size(['muon'])
#     plot_shower_size(['electron'])
    plot_shower_size_distributions()
