Station offsets
---------------

The scripts here are to be used to look at changes in offsets between
different stations. First the arrival times in detectors are corrected
using the detector offsets determined in `150416_offset_drift`. Then all
coincidences between two stations are taken and the time differences
(between the first hit detectors, corrected with detector offsets) are
calculated. The fistribution of these time differences is then fitted by
a Gauss, the mean of which is the station offset which can be used when
reconstructing coincidences.

Currently the station offsets are determined per month of data. Smaller
and larger periods will also be looked at to determine the minimum
required number of events/time for enough data for a good fit.

Besides determining the offsets station calibration and summary data is
also looked at to possibly reveal the causes of fluctuations in the
offsets.


Issues
------

Each station (with data) shows a big change in offset around timestamps
1.32-1.34 (*10^9). This is caused by the Tijdtest tests during which the GPS of station 501 was temporarily used by the test stations and 501 used a temporary GPS in the window sill, which provided a bad view of the sky.


Plot legend
-----------

- Black/Green/Blue
    These are the detector offsets for detector 1, 3, and 4, relative to
    detector 2.
- Red
    The station offset
- Shaded area
    The positive side is the average number of events per day for the
    station in question, the negative side is the same for the reference
    station (501).
- Squares
    Indicate times at which the GPS position changed, purple is for the
    reference station, gray for the station in question.
- Triangles
    Indicate times at which the PMT voltages changed, purple is for the
    reference station, gray for the station in question.
