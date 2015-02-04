from __future__ import division

from numpy import mean
from artist import Plot


if __name__ == '__main__':

    led_ph = [1, 155, 193, 155, 219, 233, 239, 169, 322, 160, 230,
              240, 285, 208, 222, 262, 174, 319, 168, 210, 216,
              162, 130, 213, 166]

    led_pi = [1, 2.43, 3.15, 2.48, 3.18, 3.60, 3.70, 2.72, 5.09, 2.49, 3.66,
              3.57, 4.51, 3.15, 3.49, 3.81, 2.64, 4.93, 2.72, 3.13, 3.27,
              2.55, 2.07, 3.40, 2.93]

    multi_led = [((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24), 5050, 86.50),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22), 4723, 73.61),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20), 4396, 68.58),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 3950, 61.43),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 3560, 55.46),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), 3150, 49.00),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 2686, 42.50),
                 ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 2140, 34.34),
                 ((1, 2, 3, 4, 5, 6, 7, 8), 1746, 28.13),
                 ((1, 2, 3, 4, 5, 6), 1224, 20.36),
                 ((1, 2, 3, 4), 716, 11.43),
                 ((1, 2), 318, 5.00)]

    signals_ph = [ph for fibers, ph, pi in multi_led]
    signals_pi = [pi for fibers, ph, pi in multi_led]
    sum_signals_ph = [sum(led_ph[fiber] for fiber in fibers) for fibers, ph, pi in multi_led]
    sum_signals_pi = [sum(led_pi[fiber] for fiber in fibers) for fibers, ph, pi in multi_led]

    ratio = mean([pi/ph for ph, pi in zip(led_ph[1:], led_pi[1:])])

    graph = Plot()
    graph.scatter(sum_signals_ph, signals_ph)
    graph.plot([0, 5500], [0, 5500], mark=None)
    graph.set_xlabel('Sum individual LED pulseheights [mV]')
    graph.set_ylabel('Multiple-LED pulseheight [mV]')
    graph.save_as_pdf('linearity_nikhef_final_ph')

    graph = Plot()
    graph.scatter(sum_signals_pi, signals_pi)
    graph.plot([0, 100], [0, 100], mark=None)
    graph.set_xlabel('Sum individual LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseintegrals [nVs]')
    graph.save_as_pdf('linearity_nikhef_final_pi')

    graph = Plot()
    graph.scatter(signals_pi, signals_ph)
    graph.scatter(led_pi[1:], led_ph[1:])
    graph.plot([0, 5500 * ratio], [0, 5500], mark=None)
    graph.set_xlabel('Multiple-LED pulseintegrals [nVs]')
    graph.set_ylabel('Multiple-LED pulseheights [mV]')
    graph.save_as_pdf('linearity_nikhef_final_ph_pi')
