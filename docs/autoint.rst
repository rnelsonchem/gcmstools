Process Sample Data
###################

Put all of your data files in a folder that must be called 'data'. Once you've
done this, run the program 'data.py' to process every AIA data file in that
folder using the calibration information that was determined from the steps
above. 

This program opens the AIA file for the sample and performs non-negative least
squares analysis of the full data set using the reference spectra that are
listed in the 'reference\_files.txt' file. Using the calibration information
that was determined above, it finds the concentrations of those components in
the sample data. For every reference compound that has associated calibration
information, a plot is generated that overlays the TIC (gray) and extracted
reference fit (blue). The title of the plot provides the calibrated
concentration information. Visual inspection of these files is recommended. 

This file also accepts the same command line arguments as 'calibration.py'
from the section above. You will be warned if you try to analyze your data
with different background information than the calibration samples. This may
not impact your data much, but it is good to know if you are doing something
different.

This file also generates another HDF5 file called 'data.h5', which contains
the integration and concentration information for every component. This
information is identical to what is printed on the extraction plots above.
However, this tabular form of the data is a bit more convenient for comparing
many data sets. See the Calibration section for a recommended HDF5 file
viewer.


