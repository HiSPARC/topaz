"""Width of dt distribution vs distance

Fokkema 2012 and Bosboom 2011 found that 1 ns / m fits the data.
For me 1.17 ns / m seems to be a better fit.
Partially explained by more stations used in the analysis,
with increased maximum distance. At higher distances the width increases due
to shower front shape and rise time are more pronounced.
At low distance (2 m) the width is still present due to small low density
showers and angled showers.

Might need a better fit than linear to account for the changing
contributions.

Data

    ref  num  dis  wid
    501  510    2    7
    501  502   90   88
    501  503  139  139
    501  504  271  296
    501  505  232  273
    501  506  158  170
    501  508   53   56
    501  509  353  408
    502  503  222  235
    502  504  360  405
    502  505  247  275
    502  506  246  264
    502  508  124  123
    502  509  390  463
    502  510   90   88
    503  504  142  148
    503  505  329  393
    503  506  122  122
    503  508  152  157
    503  509  266  309
    503  510  138  141
    504  505  408  499
    504  506  163  171
    504  508  266  297
    504  509  305  348
    504  510  271  300
    505  506  245  286
    505  508  187  214
    505  509  581  741
    505  510  234  273
    506  508  127  137
    506  509  386  464
    506  510  159  170
    508  509  394  462
    508  510   56   54
    509  510  351  411

"""
from numpy import sqrt, array

from artist import Plot

from scipy.optimize import curve_fit

def lin(x, a, b):
    return x * a + b

def plot_distance_width():
    plot = Plot()
    d = [2, 90, 139, 271, 232, 158, 53, 353, 222, 360, 247, 246, 124, 390, 90,
         142, 329, 122, 152, 266, 138, 408, 163, 266, 305, 271, 245, 187, 581,
         234, 127, 386, 159, 394, 56, 351]
    s = [7, 88, 139, 296, 273, 170, 56, 408, 235, 405, 275, 264, 123, 463, 88,
         148, 393, 122, 157, 309, 141, 499, 171, 297, 348, 300, 286, 214, 741,
         273, 137, 464, 170, 462, 54, 411]
    popt, pcov = curve_fit(lin, d, s, p0=(1.1, 1), sigma=array(d) ** 0.3)
    print popt, pcov
    plot.scatter(d, s)
    plot.plot([0, 600], [0, 600], mark=None, linestyle='gray')
    plot.plot([0, 600], [lin(0, *popt), lin(600, *popt)], mark=None)
    plot.set_xlimits(min=0, max=600)
    plot.set_ylimits(min=0, max=700)
    plot.set_xlabel(r'Distance [\si{\meter}]')
    plot.set_ylabel(r'Width of dt distribution [\si{\ns}]')
    plot.save_as_pdf('plots/distance_v_width')


if __name__ == "__main__":
    plot_distance_width()
