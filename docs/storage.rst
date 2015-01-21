Data Storage
############

Processed data files can be stored on-disk using the ``HDFStore`` object
located in the ``gcmstools.datastore`` module. Not only does this create a
convenient storage solution for processed data sets, it is also necessary when
running calibrations on a group of related data sets. The file is a `HDF
file`_, which is an open-source high performance data storage container
optimized for numerical data. Creation and manipulation of this file is
controlled using a combination of two Python libraries: `PyTables`_ and
`Pandas`_. PyTables provides a high-level interface to create and modify HDF
files, and Pandas is a very powerful package for working with tabular data.
Both of these project have extensive documentation of their many advanced
features, so little detail on their usage is provided here.

.. _HDF file: http://www.hdfgroup.org/HDF5/
.. _PyTables: http://www.pytables.org/moin 
.. _Pandas: http://pandas.pydata.org/

Create/Open the Container
-------------------------

A *gcmstools* ``HDFStore`` object can be created without any arguments, and in
which case, it automatically creates a HDF storage file called "data.h5". If
this file already exists, it will open that file for appending or
modification. If you want to have more than one data file, you can also pass
in a custom data file name as the first argument to the object creation. 

.. code::

    In : from gcmstools.datastore import HDFStore

    In : h5 = HDFStore()
    
    # Equivalent to above, change name if desired, you don't need to do both
    In : h5 = HDFStore('data.h5') 

Closing the File
----------------

In general, you will want to close the HDF file when you're done. This is not
necessary, but it does ensure that the file gets properly recompressed, which
saves some disk space.

.. code::

    In : h5.close() # Only do this when you're done

Adding Data
-----------

Added files to this storage container is done using the ``append_files``
method, which can take either a single data object or a list of objects, if
you have many objects to add at one time. It is not necessary to reference
and/or fit the data in any way before storage; however, the calibration
process will not work properly if you don't reference/fit the data.

.. code::

    In : h5.append_files(data)
    HDF Appending: datasample1.CDF

    In : h5.append_files([otherdata1, otherdata2])
    HDF Appending: otherdata1.CDF
    HDF Appending: otherdata2.CDF

.. _procfiles:

Viewing the File List
---------------------

You can see a list of the files that are stored in this file by viewing the
``files`` attribute, which is a Pandas DataFrame. 

.. code::

    In : h5.files
              name         filename
    0  datasample1  datasample1.CDF
    1  otherdata1   otherdata1.CDF
    2  otherdata2   otherdata2.CDF

There are two name columns in this table: "name" and "filename". The latter is
the full file and path name as given when the GcmsFile object was created.
Keep in mind that the path information may not be correct if you've moved the
location of this storage file. In order to efficiently store the data on disk,
the full file name is internally simplified the "name". This simplification
removes the path and file extension from the file name. In addition, it
replaces all ".", "-", and spaces characters with "_". If the file name starts
with a number, the prefix "num" is added. 

.. warning::

    You will encounter problems if two or more file names simplify to the same
    "name".  However, if you're file naming system does not produce unique file
    names for different data sets, you will most certainly have more problems in
    the long run than just using these programs. 

Extracting Stored Data
----------------------

You can extract data from the storage file using the ``extract_data`` method.
This function takes one argument which is the name of the dataset that you
want to extract. This name can be either the simplified name or the full
filename (with or without the path). The extracted data is the same file
object type as you stored originally. 

.. code:: 

    In : extracted = h5.extract_data('datasample1')

    In : extratced.filetype
    Out: "AiaFile"


Stored Data Tables
------------------

This HDF data file may contain a number of Pandas data tables (DataFrames)
with information about the files, calibration, etc. A list of currently
available tables can be obtained from the ``pdh5`` attribute of the
``HDFStore`` object. (Note: you won't see these attributes using :ref:`tab
completion <ipytab>`. You must directly inspect ``pdh5``.

.. code::

    In : h5.pdh5
    Out: 
    <class 'pandas.io.pytables.HDFStore'>
    File path: data.h5
    /calibration            frame        (shape->[6,8]) 
    /calinput               frame        (shape->[30,9])
    /datacal                frame        (shape->[49,6])
    /files                  frame        (shape->[1,2]) 

To view these tables, just append the table name after ``pdh5``.

.. code::

    In : h5.pdh5.calibration
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

More information on using these tables is provided in :doc:`appendB`.


