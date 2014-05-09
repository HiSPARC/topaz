# TijdTest Tests

Try to determine the time differences between difference HiSPARC II
Master (HIIM) boxes. Test them one by one, using one specific HIIM (62)
as reference point to the rest. Connect the two HIIM boxes to Eee boxes.
Connect each to a GPS that is close to the other (501 and testGPS). For
the first test, calibrate the GPS (GPSMon) and store the locations (on
paper) to input in each next HIIM, to keep that constant, since the GPS
does not move and enable it to run in Overdetermined Clock mode. After
running each box for about a day compare the timestamp differences.
Check if there is a correlation between firmware versions, batches, GPS,
...

Give the reference HIIM station the station number 95 (Tijdtest) and the
variable station station number 94 (Tijdtest2). Make careful note of
when and which HIIM was connected and also its firmware versions
(DSPMon) and which port was used to trigger.

Trigger both HIIMs by the same pulse generator, using the same (short)
cable lengths.

- Try triggering on external trigger, maybe let this run for a day (to
  confirm David's earlier tests).
- Try manually shifting the GPS position of one of the GPSs by 100
  meters and see what happens.
- Try connecting a Slave to a Master and then triggering via the Slave.
- Try swapping the GPSs, the trigger cables, ..
- Measure the cable delays of those used for triggering

    - Connect to same pulse generator
    - Conenct to same oscilloscope
    - Swap cable/ports to find differences

- Using a [GPSSource S14-A GPS
Splitter](http://www.gpssource.com/products/gps-splitter/46) to split
the GPS signal from one antenna to multiple cables/HiSPARC Masters.
