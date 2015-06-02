# 150602 Muonlab tests

## Reasoning

prof. Frank Linde wants to use scintillator detectors to detect muons
passing through material. By placing a detector at the top and one at
the bottom you can detect the same muon in both detectors. However a
test resulted in to many coincidences between two detectors placed at
large altitude difference. We believe this excess may be caused by air
showers hitting both detectors but with different particles (not
detecting the same muon). This effect will become more important the
further the detectors are apart because the opening angle of the two
detectors becomes smaller.


## Tests

On 2015/05/28 a test with two muonlab detectors was started. Test
station 99 was used to capture the data. One detector was placed on the
roof of the Nikhef between detectors 1 and 4 of stations 501 and 510.
The second muonlab detector was placed underneath the first in the
HiSPARC office. The test ran until 2015/06/02 hh:mm (GPS time).
Distance between detectors: 4? meter.

After this the second detector was placed on the ground floor in the
inner court of the Nikhef, close to the building, still relatively close
to being underneath the first detector. This test was started on
2015/06/02 hh:mm.
Distance between detectors: 20? meter.


## Data processing

The scripts here download this data, look for coincidences between the
muonlab events and the HiSPARC stations and then filter events in and
not in coincidence.


## Results

The events with high pulseheights are often in coincidence with an air
shower. The time difference distribution is slightly different, for
events not in coincidence the mean is .... For events in coincidence the
mean is slightly closer to 0. This could be caused by inclined air
showers, because then the distance between the two detectors is less
important because different particles are detected.
