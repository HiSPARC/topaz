# Correlation between detector efficiency and outside temperature

Look for correlations between the value of the MPV (measure for detector efficiency) and the temperature of the detector (i.e. outside temperature corrected with solar radiation data, if available).


## Why

We want to estimate the number of particles in a detector by fitting the MPV of the pulse integrals. By fitting the MPV for short periods (e.g. 3 hours) we observe changes in the value of the MPV which correlate to the outside temperature. When the correlation coefficient is obtained all pulse integral values can be corrected for the temperature at the time of the event.


## How

- Fit the MPV for multiple short periods per day
- Determine correlation between temperature and MPV.
- Correct pulse integrals depending on the temperature.


## Notes

Compare the pulse integral histograms from before and after the correction.


## References

- de Vries 2012 Search for a correlation between HiSPARC cosmic-ray data and weather measurements
- Bartels 2012 An Analysis of the MPV and the Number of Events per Unit Time
- ET 9107B PMT specifications
- ELJEN EJ200 Scintillator specifications
