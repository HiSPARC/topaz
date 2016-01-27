# 140315 Check LED fiber quality

Setup
-----

Pulse generator set for a puls to -3 V, with 0 V baseline, 20 ns pulse
width and .1 s between pulses.

The oscilloscope was set to trigger on the pulse from the PMT (or on
pulse from sync from pulse generator). And using acquire we took the
average of 16-64 pulses to get a more stable pulse height

Reference PMT serial number 19605 set to 1700 V using fiber 012 gives a
pulse height of 370 mV.

Tests done together with Jan Oldenziel.


Test results
------------

    LED Fiber   Pulseheight
    #01         225 mV
    #02         300 mV
    #03         225 mV
    #04         320 mV
    #05         250 mV
    #06         350 mV
    #07         375 mV
    #08         370 mV
    #09         340 mV
    #10         325 mV
    #11         300 mV
    #12         350 mV

    #13         325 mV
    #14         350 mV
    #15         350 mV
    #16         350 mV
    #17         325 mV
    #18         350 mV
    #19         350 mV
    #20         350 mV
    #21         330 mV
    #22         310 mV
    #23         350 mV
    #24         350 mV
