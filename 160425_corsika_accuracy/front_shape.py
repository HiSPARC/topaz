r"""

Extracted points from the tex file:

for file in *.tex;
    do sed -n '/addplot\[mark=\*,solid/,/\}/p' $file > stripped/${file};
done;

"""

from glob import glob

from numpy import arange, count_nonzero, loadtxt, median, zeros
from scipy.optimize import curve_fit

from artist import Plot

PATH = '/Users/arne/Datastore/corsika_accuracy/stripped/'


def front_shape(r, a, b):
    return a * (r ** b - 20 ** b)


def plot_front_shapes():
    r = [20, 29, 41, 58, 84, 120, 171, 245, 350, 501]
    fit_r = arange(0, 510, 5)
    for particle in ['gamma', 'proton', 'iron']:
        for energy in ['15.0', '15.5', '16.0', '16.5', '17.0']:
            files = glob(PATH + '{}_E_{}*'.format(particle, energy))
            if not len(files):
                continue

            t = zeros((len(r), len(files)))

            for i, file in enumerate(files):
                detected_t = loadtxt(file, usecols=(1,))
                t[:, i][:len(detected_t)] = detected_t

            t_src = t.copy()
            for j in range(1, len(t)):
                t[j] -= t[0]
            t[0] -= t[0]
            mean_t = t.mean(axis=1)
            try:
                min_limit = 3
                min_efficiency = 0.9
                limit = min_limit + next(i for i, ti in enumerate(t_src[min_limit:])
                                         if not count_nonzero(ti) > min_efficiency * len(files))
            except:
                limit = len(r)

            plot = Plot()
            plot.scatter(r[:limit], mean_t[:limit],
                         yerr=t.std(axis=1)[:limit], xerr=[10] * limit)
            plot.scatter(r[:limit], median(t, axis=1)[:limit], mark='x')

            popt, pcov = curve_fit(front_shape, r[:limit], mean_t[:limit])

            plot.plot(fit_r, front_shape(fit_r, *popt), linestyle='gray', mark=None)
            print(particle, energy, popt)
            plot.set_ylimits(-10, 130)
            plot.set_xlimits(-10, 510)
            plot.set_ylabel(r'Delay [\si{\ns}]')
            plot.set_xlabel(r'Core distance [\si{\meter}]')
            plot.save_as_pdf('plots/front_shape/{}_{}.pdf'.format(particle, energy))


if __name__ == "__main__":
    plot_front_shapes()
