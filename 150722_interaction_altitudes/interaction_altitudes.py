from artist import Plot
import tables
from numpy import log10, median, percentile

# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def plot_interaction_height():
    plot = Plot(axis='semilogy')
    with tables.open_file(OVERVIEW, 'r') as overview:
        sims = overview.get_node('/simulations')
        for e in set(log10(sims.col('energy'))):
            median_altitude = []
            min_altitude = []
            max_altitude = []
            zeniths = sorted(set(sims.read_where('(log10(energy) == e) & '
                                                 '(particle_id == 14)',
                                                 field='zenith')))
            for z in zeniths:
                selection = sims.read_where('(log10(energy) == e) & '
                                            '(zenith == z) & '
                                            '(particle_id == 14)')
                interaction_altitudes = selection['first_interaction_altitude']
                median_altitude.append(median(interaction_altitudes))
                min_altitude.append(percentile(interaction_altitudes, 16))
                max_altitude.append(percentile(interaction_altitudes, 84))
            if len(zeniths):
                plot.plot(zeniths, median_altitude)
                plot.shade_region(zeniths, min_altitude, max_altitude,
                                  color='lightgray,semitransparent')
                plot.add_pin('%.1f' % e, relative_position=0)
    plot.set_ylabel(r'First interaction altitude [m]')
    plot.set_xlabel(r'Zenith [\si{\radian}]')
    plot.save_as_pdf('interaction_altitude')


if __name__ == "__main__":
    plot_interaction_height()
