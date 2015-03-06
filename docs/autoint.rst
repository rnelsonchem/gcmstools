Batch Processing
################

All of the previous steps can be automated using the ``proc_data`` fuction
located in the ``gcmstools.general`` module. 

.. code::

    In : from gcmstools.general import proc_data

This function only has two required arguments: 1) the path to the folder that
contains *all* of the GCMS files and 2) the name of the data file that you'd
like to generate. In this example, our data is in the folder "data" and our processed data file is called "data.h5". 

.. code::

    In : proc_data('data/', 'data.h5')
    ... # Lots of stuff will get printed at this point.


The ``proc_data`` function accepts numerous keyword arguments to allow some
process control.

* *filetype='aia'* : This flag can be used to control the type of GCMS objects
  used for processing the data in your folder. The default value ``'aia'``
  uses the ``AiaFile`` object. See :doc:`basics` for detailed information.

* *reffile=None* : Pass the name of a reference file for referencing your GCMS
  data. The default is ``None``, so no referencing will be done. Otherwise,
  the reference object will be determined by the file extension. For example,
  ``reffile='ref_specs.txt'`` will create a ``TxtReference`` object using the
  file "ref_specs.txt" (which must exist of course). See :doc:`fitting` for
  more information.

* *fittype=None* : Set the fitting type to use for fitting the GCMS data. See
  :doc:`fitting` for detailed information. The valid choices are: 
  
    * ``'nnls'`` for non-negative least squares fitting.

* *calfile=None* : Pass in the name of a calibration csv file to generate
  calibration curves and integrate the data. For example,
  ``calfile='calibration.csv'`` will calibrate your data using the information
  in the csv file "calibration.csv". See :doc:`calibration` for detailed
  information, especially on the expected structure of the csv file.
  
* *picts=False* : Set this argument to true if you want to generate pictures
  of your calibration curves and data fits. These calibration curves will be
  placed in the folder "cal", and plots of integrals with concentrations will
  be place in the folder "proc". Be careful! All files in these folders will
  be deleted before the plots are generated. Also, if you have a lot of data
  files, this process can be very slow. It is possible to view these plots
  after processing.  See :doc:`calibration` for detailed information.

* *chunk_size=4* : This sets the number of files that will be processed at any
  given time. This keeps the total number of opened GCMS files to a minimum,
  which is important if you have a large number of files to process. You
  probably don't need to change this.
  
* *multiproc=False* : Setting this argument to ``True`` will use IPython's
  parallel machinery to run a lot of the processing using multiple cores on
  your processor.  Before using this command, you must start an IPython node
  cluster from the command line.  Open a new terminal, and type the following
  command::

        home>$ ipcluster start -n 2

  This will start a cluster of two (``-n 2``) nodes. You can have up to one
  node per core on your processor. Setting this number greater than the number
  of cores will result in a degradation of performance. To stop the node
  cluster, type ``Ctrl-c`` from the terminal where you started the cluster. Or
  else, you can stop it from another terminal using the following command::

        home>$ ipcluster stop

  This only works for processing the files, not for generating plots. So
  plotting your calibration data will still be very slow for a lot of data
  files.

  See `IPython's parallel documentation`_ for more information.

* This function can also accept all keyword arguments for any file type,
  reference, fitting, and calibration objects. See their documentation for
  more information.

.. _IPython's parallel documentation: http://ipython.org/
        ipython-doc/dev/parallel/


Complete Processing Command
+++++++++++++++++++++++++++

A complete version of this processing command might look like the following.

.. code:: 

    In : proc_data('data/', 'data.h5', filetype='aia', reffile='ref_spects.txt',
            fittype='nnls', calfile='calibration.csv', multiproc=True)
    ### Lot's of stuff gets printed
    ...

The HDF file "data.h5" contains all of your data. See the :doc:`storage`,
:doc:`calibration`, and :doc:`appendB` for more information on how to view and
plot these data.


