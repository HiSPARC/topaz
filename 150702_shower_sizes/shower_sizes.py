from artist import Plot
import tables
from numpy import log10, median, percentile, degrees, array, arange

# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


    plot = Plot(axis='semilogy')
def plot_shower_size(leptons=['electron', 'muon']):
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        for e in set(log10(sims.col('energy'))):
            median_size = []
            min_size = []
            max_size = []
            zeniths = sorted(set(sims.read_where('(log10(energy) == e) & '
                                                 '(particle_id == 14)',
                                                 field='zenith')))
            for z in zeniths:
                selection = sims.read_where('(log10(energy) == e) & '
                                            '(zenith == z) & '
                                            '(particle_id == 14)')
                n_leptons = selection['n_%s' % leptons[0]]
                for lepton in leptons[1:]:
                    n_leptons += selection['n_%s' % lepton]
                median_size.append(median(n_leptons))
                min_size.append(percentile(n_leptons, 16))
                max_size.append(percentile(n_leptons, 84))
            if len(zeniths):
                plot.plot(degrees(array(zeniths)), median_size, linestyle='very thin')
                plot.shade_region(degrees(array(zeniths)), min_size, max_size, color='lightgray,semitransparent')
                plot.add_pin('%.1f' % e, relative_position=0)
    plot.set_xticks([t for t in arange(0, 60.1, 7.5)])
    plot.set_ylimits(1, 1e9)
    plot.set_ylabel(r'Shower size (leptons)')
    plot.set_xlabel(r'Zenith [\si{\degree}]')
    plot.save_as_pdf('shower_sizes_%s' % '_'.join(leptons))


if __name__ == "__main__":
    plot_shower_size()
    plot_shower_size(['muon'])
    plot_shower_size(['electron'])
