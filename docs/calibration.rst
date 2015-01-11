Automated Calibration and Integration
#####################################

Calibration Data
----------------

If you have calibration data for a particular reference compound, you must
create a csv file and folder that have the same base name as the reference MS
file from above. Again, an examples are provided in this repository called
refcpd.csv and the folder refcpd. All of your calibration AIA files for this
compound need to be stored in the newly created folder. In order for these new
data files to be processed, the refcpd.csv file must be appropriately
modified. 

The csv file is a simple comma-separated text file, but again the structure is
important. The first row in this file is critical. At the end, there are two
values that define the starting and stopping time points for integration.
Change these values based on the time range that you've determined from the
TIC of a calibration run. The rest of the rows are data file information.  The
first column is the name of a calibration data file, and the second column
needs to be the concentration of the reference compound associated with that
run. You don't have to add all of the calibration files here, but if they are
not in this list, they won't be processed.  Alternatively, any line that
starts with a '#' is a comment, and will be ignored. In this way, you can
comment out samples, and add some notes as to why that sample was not used or
whatever.

Run Calibrations
----------------

Once you've updated the calibration information from above. You can run the
program 'calibration.py'. This runs through all of the reference spectra
defined in the 'reference\_files.txt' file. If a '.csv' file exists for a
particular reference file, then a calibration will be performed. 

All of the calibration data files listed in the csv file  will be processed
and a calibration curve generated. For each calibration sample, a plot of the
reference-extracted data will be generated in the calibration folder
(refcpd\_fits.png). In addition, a calibration curve plot is also generated
(refcpd\_cal\_curve.png'), which plots the integrated intensities and
calibrated intensities vs the concentrations. In addition, the calibration
information is printed on the graph for quick visual inspection. There is no
need to write down this calibration information.

This program has some important command line arguments that will change the
programs defaults. The first argument, '--nobkg', is a simple flag for
background fitting. By default, the fitting routine will select a MS slice
from the data set and use that as a background in the non-negative least
squares fitting. This procedure can change the integrated values. If you use
this flag, then a background MS will not be used in the fitting. Using a
background slice in the fitting may or may not give good results. It might be
a good idea to look at your data with and without the background subtraction
to see which is better.

The second command line argument is '--bkg\_time'. By default, the fitting
program uses the first MS slice as a background for fitting.  However, if
there is another time that looks like it might make a better background for
subtraction, then you can put that number here. 

Here's a couple of example usages of this script:

.. code::

    # This will run the calibration program with all defaults
    $ python calibration.py
    # This shuts off the background subtraction
    $ python calibration.py --nobkg
    # This sets an alternate time for the background subtraction
    # In this case, the time is set to 0.12 minutes
    $ python calibration.py --bkg_time 0.12

Another file is also generated during this process: cal.h5. This is a HDF5
file that contains all of the calibration information for each standard. Do
not delete this file; it is essential for the next step. This is a very simple
file, and there are many tools for looking at the internals of an HDF5 file.
For example, `ViTables`_ is recommended. The background
information, such as whether a background was used and the time point to use
as a background spectrum, are stored as user attributes of the calibration
table.

.. _ViTables: http://vitables.org/


