from artist import MultiPlot

from sapphire import api

sns = api.Network(force_stale=True).station_numbers()
original_base = api.LOCAL_BASE

for i in range(8):
    plot = MultiPlot(16, 1, width=r'0.67\linewidth', height=r'0.05\linewidth')
    for splot, sn in zip(plot.subplots, sns[i * 16 : (i + 1) * 16]):
        for path, color in [(original_base, 'black'), (original_base + '_old', 'red')]:
            api.LOCAL_BASE = path
            try:
                s = api.Station(sn, force_stale=True)
                if not len(s.detector_timing_offsets):
                    splot.set_empty()
                    continue
            except:
                splot.set_empty()
                continue
            splot.plot(
                s.detector_timing_offsets['timestamp'],
                s.detector_timing_offsets['offset1'],
                mark=None,
                linestyle='ultra thin, ' + color,
            )
            splot.set_axis_options('line join=round')
            splot.set_ylabel(str(sn))
    plot.set_ylimits_for_all(None, -20, 20)
    plot.set_xlimits_for_all(None, 1224201600, 1465344000)
    plot.save_as_pdf('detector_offset_set_%d' % i)
