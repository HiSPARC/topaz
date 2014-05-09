# TijdTest Problems

Notes
-----

....


Problems
--------

Installing a not-up-to-date version of HiSPARC (eg 4.8) on Windows 7 can
cause problems when updating. This is caused by the default Windows
Access Control setting and problems with the Virtual Drive.

Setting the GPS position manually:

- Start HiSPARC DAQ software to ensure firmware is loaded
- Set other settings..
- Select correct COM port in DSPMon
- Set (and Save) GPS position in DSPMon
- Choose *Stop program* (in the HiSPARC DAQ)
- Start Export Mode again to apply new settings

For some tests I accidently input the wrong GPS coordinates, resulting in
an offset of 25 meters for the best known position. This resulted in a large
standard deviation in the results. Moreover, this test (83/501/EXTb) helped
show the periodic variation caused by the gps satellite orbits (24h/12h?).

Pulse generator is not very consistent with its rate, on average it is
good, and the A and B channels are properly synced, in case of same
trigger the same port from the pulse generator was used. The pulse
arrival time difference between the A (PMT) and B (EXT) channel of the
pulse generator is ~3 ns (EXT is later). The time difference between the
two cables (T-splitter) from the A channel (PMT trigger) is 0 ns.
External trigger appears to trigger 125 ns faster than the PMT ports if
the signal arrives at the same time.

Note that I did use a wrong length (to long) cable for the external
trigger at first, but replaced this (on 111125) by a same length cable
as used for the other triggers, but still a small time difference
exists. The small time difference is probably slightly mitigated because
the PMT triggers on the first (rising) part of the pulse, while the EXT
should trigger on the 'top' of the pulse.
