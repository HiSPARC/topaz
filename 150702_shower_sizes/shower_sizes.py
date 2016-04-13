from artist import Plot
import tables
from numpy import (log10, median, percentile, degrees, array, arange,
                   histogram, logspace, linspace, mean, nan)
from scipy.optimize import curve_fit

from sapphire import CorsikaQuery

# proton = 14
# iron = 5626

OVERVIEW = '/Users/arne/Datastore/CORSIKA/corsika_overview.h5'


def f(x, a, b=1.):
    """Relation between shower size and energy

    size = 10 ** (energy ** b - a)

    """
    return (x ** b - a)


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
            sizes = percentile(n_leptons, [16, 50, 84])
            min_size.append(sizes[0] if sizes[0] else 0.1)
            median_size.append(sizes[1] if sizes[1] else 0.1)
            max_size.append(sizes[2] if sizes[2] else 0.1)
        if len(zeniths):
            plot.plot(zeniths, median_size, linestyle='very thin')
            plot.shade_region(zeniths, min_size, max_size,
                              color='lightgray, semitransparent')
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


def plot_size_energy():
    cq = CorsikaQuery(OVERVIEW)
    p = 'proton'
    plot = Plot(axis='semilogy')
    for z in cq.available_parameters('zenith', particle=p):
        zen_plot = Plot(axis='semilogy')
        shade = 'black!%f' % (100 - z)

        energies = sorted(cq.available_parameters('energy', particle=p,
                                                  zenith=z))
        sizes_m = []
        sizes_e = []
        sizes_l = []
        energies_m = []
        energies_e = []
        energies_l = []

        for e in energies:
            selection = cq.simulations(zenith=z, energy=e, particle=p)
            if median(selection['n_muon']):
                sizes_m.append(median(selection['n_muon']))
                energies_m.append(e)
            if median(selection['n_electron']):
                sizes_e.append(median(selection['n_electron']))
                energies_e.append(e)
            if median(selection['n_muon'] + selection['n_electron']):
                sizes_l.append(median(selection['n_muon'] + selection['n_electron']))
                energies_l.append(e)

        # Plot data points
        zen_plot.scatter(energies_m, sizes_m, mark='+')
        zen_plot.scatter(energies_e, sizes_e, mark='x')
        zen_plot.scatter(energies_l, sizes_l, mark='square')
        plot.scatter(energies_l, sizes_l, mark='square', markstyle=shade)

        # Fit
        initial = (10.2, 1.)
        popt_m, pcov_m = curve_fit(f, energies_m, log10(sizes_m), p0=initial)
        popt_e, pcov_e = curve_fit(f, energies_e, log10(sizes_e), p0=initial)
        popt, pcov = curve_fit(f, energies_l, log10(sizes_l), p0=initial)

        # Plot fits
        fit_energies = arange(10, 20, 0.25)
        sizes = [10 ** f(e, *popt_m) for e in fit_energies]
        zen_plot.plot(fit_energies, sizes, mark=None, linestyle='red')

        sizes = [10 ** f(e, *popt_e) for e in fit_energies]
        zen_plot.plot(fit_energies, sizes, mark=None, linestyle='blue')

        sizes = [10 ** f(e, *popt) for e in fit_energies]
        zen_plot.plot(fit_energies, sizes, mark=None)
        plot.plot(fit_energies, sizes, mark=None, linestyle=shade)

        zen_plot.set_ylimits(1, 1e9)
        zen_plot.set_xlimits(10.5, 18.5)
        zen_plot.set_ylabel(r'Shower size [number of leptons]')
        zen_plot.set_xlabel(r'Shower energy [log10(E/eV)]')
        zen_plot.save_as_pdf('shower_size_v_energy_%.1f.pdf' % z)
    plot.set_ylimits(1, 1e9)
    plot.set_xlimits(10.5, 18.5)
    plot.set_ylabel(r'Shower size [number of leptons]')
    plot.set_xlabel(r'Shower energy [log10(E/eV)]')
    plot.save_as_pdf('shower_size_v_energy')
    cq.finish()


if __name__ == "__main__":
    plot_shower_size()
    plot_shower_size(['muon'])
    plot_shower_size(['electron'])
    plot_shower_size_distributions()
    plot_size_energy()
