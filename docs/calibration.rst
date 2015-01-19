Calibration and Integration
###########################

Calibration Object
------------------

The calibration class ``Calibrate`` is defined in the
``gcmstools.calibration`` module. This object must have access to an HDF
storage file that contains *all* of your data to be processed. The default
object creationg tries to open a file "data.h5"; however, an alternate name
can also be passed in on construction to open a different HDF file. 

.. code::

    In : from gcmstools.calibration import Calibrate

    In : cal = Calibrate() # Opens 'data.h5' by default

    In : # Or: cal = Calibrate('other.h5') if you have a different name

Calibration Information File
----------------------------

In order to integrate your GCMS data, you must first create a csv file
containing all of the relevant calibration information. Again, the structure
of this file is very important, so an example, "calibration.csv", is contained
with the sample data.

.. code::

    In : from gcmstools.general import get_sample_data

    In : get_sample_data("calibration.csv")

The first row in this csv file is critical, and it must look like this::

    Compound,File,Concentration,Start,Stop,Standard,Standard Conc

Each row after this describes a set of calibration information that you'd like
to use for The columns of this file are as follows:

* *Compound*: The name of the compound that you are calibrating. This *must*
  correspond to one of the compound names (case-sensitive) used when
  referencing and fitting the GCMS file. See the :doc:`relevant page
  <fitting>` for more information.

* *File*: This is the name of the data set that you'll use for this compound
  at a particular, known concentration. Again, this filename can be the full
  filename (with or without the path) or the simplified name. See the
  :ref:`files attribute <procfiles>` section of the HDFStore docs for more
  info.

* *Concentration*: This is the concentration of *Compound* in *File*. This
  should only be a number. Do not include units. All of the concentrations
  should be in the same units, and keep in mind that all calibration and
  integration data will then be in that same unit of measurement. 

* *Start* and *Stop*: These are the integration range start and stop times in
  minutes. Again use only numbers, no units.

* *Standard* and *Standard Conc*: If there is an internal standard used in
  this file, you should provide the name and concentration in these columns.
  Again, the standard name should have been defined when referencing your GCMS
  data set, and do not include units with the concentration. Make sure your
  concentration units are the same as the reference compound to avoid
  confusion.

You can add extra columns to this table without penalty, in case you need to
add additional information to this table. You can also comment out lines by
starting a line with a ``#`` character. This is useful if you want to ignore
a bad data point without completely removing the line from the calibration
file.

Run Calibrations and Integrations
---------------------------------

Calibration Curves
++++++++++++++++++

The calibration curves can be generated using the ``curvegen`` method of the
``Calibrate`` object. This function must be called with the name of your
calibration file. In this example, that filename is "calibration.csv".

.. code::

    In : cal.curvegen('calibration.csv')
    Calibrating: benzene
    Calibrating: phenol
    ...

    In :

This process creates two new tables as attributes to your calibration object,
``calinput`` and ``calibration``. The former table is simply your input csv
information with columns appended for the concentrations ("conc") and
integrals ("integral") used for generating the calibration curve. If no
internal standard is defined, then "conc" will be the same as the compound
concentration you used in the input file. If an internal standard was defined,
then "conc" and "integral" will be these values divided by the corresponding
internal standard values. These tables also stored in the HDF file as well, if
you want to check them at a later date.

The calibration table contains all of the newly created calibration curve
information, such as slope, intercept, r value, etc.

.. code::

    In : cal.calibration
    Out: 
                   Start  Stop  Standard         slope      intercept         r  \
    Compound                                                                      
    benzene          2.9   3.5       NaN  38629.931565 -367129.586850  0.998767   
    phenol          14.6  15.1       NaN  30248.192619   65329.897933  0.999136   
    ...

                          p       stderr  
    Compound                              
    benzene        0.000052  1108.344872  
    phenol         0.000030   726.257380  
    ...

Plotting Calibrations
+++++++++++++++++++++

By default, no plots are generated for these calibrations. There are a couple
of ways to get some plots of the calibration data.

#. ``cal.curvegen('calibration.csv', calfolder='cal', picts=True)`` : This
   method will auto generate pictures for all of the calibration compounds and
   place them in a folder defined by the keyword argument ``calfolder``. This
   argument is optional, if you don't mind the default folder name of "cal".
   Be careful! This will delete this folder before generating new plots, so if
   this folder exists, make sure it is clear of important data.

#. ``cal.curveplot('benzene')`` : This method will generate a plot of the
   benzene calibration information and save it to the current folder. There
   are several keyword arguments to this function:

   * ``folder='.'`` : This sets the folder where the picture will be saved. By
     default it is the current directory.
   
   * ``show=False`` : Change this value to ``True`` if you want an interactive
     plot window to be displayed. Default is ``False``.

   * ``save=True`` : Save the calibration plot to the folder. 

   If both ``save`` and ``show`` are set to ``False``, nothing will happen.
   
   Of course, this function must be done after a call to ``curvegen``, but it
   does provide a method to look at calibration data from an previously
   processed HDF file without rerunning the calibration.


Integrating Data
++++++++++++++++

Once the calibration curves have been generated, you can integrate all of the
remaining data in the HDF file using the ``datagen`` method of the
``Calibrate`` object.

.. code:: 

    In : cal.datagen()
    Processing: datasample1.CDF
    Processing: otherdata1.CDF
    Processing: otherdata2.CDF
    ...

After processing, another data table attributed (``datacal``) is created and
saved to the HDF file. 

.. code::

    In : cal.datacal
    Out: 
                                  benzene       phenol   ...
    name                                                               
    datasample1               4239.070627    58.336917   ...
    otherdata1                5475.778519    20.401981   ...
    otherdata2                4355.094930    19.171877   ...
    ...

Plotting Integrals
++++++++++++++++++

By default, no plots are generated for the integrals. If you'd like to see
plots of the integrals, there are a couple of methods.

#. ``cal.datagen(datafolder='data', picts=True)`` : This method will auto
   generate pictures for all of the calibration compounds and place them in a
   folder defined by the keyword argument ``datafolder``. This argument is
   optional, if you don't mind the default folder name of "data".  Be careful!
   This will delete this folder before generating new plots, so if this folder
   exists, make sure it is clear of important data.

#. ``cal.dataplot('benzene', 'datasample1')`` : This method will generate a
   plot of the benzene integral for 'datasample1' and save it to the current
   folder. There are several keyword arguments to this function:

   * ``folder='.'`` : This sets the folder where the picture will be saved. By
     default it is the current directory.
   
   * ``show=False`` : Change this value to ``True`` if you want an interactive
     plot window to be displayed. Default is ``False``.

   * ``save=True`` : Save the calibration plot to the folder. 

   If both ``save`` and ``show`` are set to ``False``, nothing will happen.
   
   Of course, this function must be done after a call to ``datagen``, but it
   does provide a method to look at calibration data from an previously
   processed HDF file without rerunning the calibration and data integration
   functions.
