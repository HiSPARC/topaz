from numpy import linspace

from artist import Plot

from fit_curve import fit_curve, ice_cube_pmt_p1
from data_senstech_integral import M_PH as senstech_m_ph, E_PH as senstech_e_ph
from data_nikhef_final_integral import M_PH as nikhef_m_ph, E_PH as nikhef_e_ph


if __name__ == '__main__':

    popt, perr = fit_curve(senstech_m_ph, senstech_e_ph)
    print popt, perr

    fit = (r"$\mathrm{ln}V_{\mathrm{in}}=\mathrm{ln}V + "
           r"\frac{p_0\left(\frac{V}{p_1}\right)^{p_2}}"
           r"{\left(1-\frac{V}{p_1}\right)^{\frac{1}{4}}}$"
           r", \scriptsize{($p_0=%.1f$, $p_1=%d$, $p_2=%.1f$)}") % (popt[0], 9000, popt[1])

    graph = Plot(width=r'.67\linewidth', height=r'.67\linewidth',)
    graph.set_label(fit, location='upper left')
    graph.scatter(senstech_e_ph, senstech_m_ph, mark='*')
    graph.scatter(nikhef_e_ph, nikhef_m_ph, mark='o')
    inputs = linspace(min(senstech_m_ph), max(senstech_m_ph), 500)
    graph.plot([ice_cube_pmt_p1(input, *popt) for input in inputs], inputs, mark=None)
    graph.plot([0, 6000], [0, 6000], mark=None, linestyle='gray')
    graph.set_xlimits(0, 6000)
    graph.set_ylimits(0, 6000)
    graph.set_axis_equal()
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.save('linearity_compared')
