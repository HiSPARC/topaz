from artist import Plot
import tables
from numpy import log10, median, percentile

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview_150624.h5'

def plot_shower_size():
    plot = Plot(axis='semilogy')
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        for e in set(log10(sims.col('energy'))):
            median_size = []
            min_size = []
            max_size = []
            zeniths = sorted(set(sims.read_where('log10(energy) == e')['zenith']))
            for z in zeniths:
                selection = sims.read_where('(log10(energy) == e) & '
                                            '(zenith == z) & '
                                            '(particle_id == 14)')
                n_leptons = selection['n_electron'] + selection['n_muon']
                median_size.append(median(n_leptons))
                min_size.append(percentile(n_leptons, 16))
                max_size.append(percentile(n_leptons, 84))
            plot.plot(zeniths, median_size)
            plot.shade_region(zeniths, min_size, max_size, color='lightgray,semitransparent')
            plot.add_pin('%.1f' % e, relative_position=0)
    plot.set_ylabel(r'Shower size (leptons)')
    plot.set_xlabel(r'Zenith [\si{\degree}]')
    plot.save_as_pdf('shower_sizes')


if __name__ == "__main__":
    plot_shower_size()
