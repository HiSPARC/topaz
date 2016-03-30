# Coincidence rate versus distance between stations

Here we look for station pairs which have a certain distance to each other.
Then we find out when they were both working. For each of those periods
coincidence data is downloaded. The number of coincidences divided by the
total time both were on is then the coincidence rate.

## Coincidence window

For the ESD a coincidence window of 2µs was chosen. This corresponds to
approximately 600m at light speed. For horizontal showers this would be the
maximum distance between stations that would be included. Other experiments
often use a zenith limit of 60° (which gives one solid angle of sky coverage).
At 60° the maximum distance (assuming flat shower front and no timing offsets)
would be: Δt / sin(θ) = d, for θ = 60° this gives 690m. When reducing the
angle further the possible distance becomes larger.

So for stations further appart than 600m the zenith angle acceptance it reduced
This reduces the coincidence rate.


## Bad stations and pairs

Several stations/station pairs have deviating rates. In some cases these
can be explained.

'bad' stations:

- 20001 - GPS has bad sky coverage (possibly UTC?)
- 20002 - station has been moved around 2012
- 20003 - station has been moved around 2012
- 13007 - bad PMT calibration, to many events
- 2103 - unknown, possibly UTC?
- 1010 - partly 2 detectors, others not working well
- 1001 - only 2 detectors, not 4
- 507 - inside Nikhef, much lower event rate
- 22 - Moved to different location


Pairs with very few coincidences (pair, n coincidences):

- (8102, 8105) 2 - 8102 has very little good data
- (13002, 13006) 2 - 8 km apart, only background
- (13003, 13008) 1 - 13008 only has a week of data
- (13005, 13008) 3 - 13008 only has a week of data
- (13102, 13104) 4 - 13104 started at end of January 2016
- (13103, 13104) 2 - 13104 started at end of January 2016
