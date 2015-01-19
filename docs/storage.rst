Data Storage
############

Processed data files can be stored on-disk for later reuse using the
``HDFStore`` object located in the ``gcmstools.datastore`` module. Not only
does this create a convenient storage solution for processed data sets, it is
also necessary when running calibrations on a group of related data sets. This
file is stored on-disk in as a `HDF file`_, which is an open-source high
performance data storage container optimized for numerical data. Creation and
access of this file is controlled using a combination of two Python libraries:
`PyTables`_ and `Pandas`_. PyTables provides a high-level interface to the HDF
file types, and Pandas is a very powerful package for working with tabular
data. Both of these project have extensive documentation on their use.

A *gcmstools* ``HDFStore`` object can be created without any arguments, and in
this case, it automatically creates a file called "data.h5". If this file
already exists, it will open that file for appending or modification. If you
want to have more than one data file, you can also pass in a custom data file
name as the first argument to the object creation. 

.. code::

    In : from gcmstools.datastore import HDFStore

    In : h5 = HDFStore()

    In : # Or: h5 = HDFStore('data.h5') or whatever file name you'd like

Added files to this storage container can be done with the ``append_files``
method, which can take either a single data object or a list of objects, if
you have many objects to add at one time. 

.. code::

    In : h5.append_files(data)
    HDF Appending: datasample1.CDF

    In : h5.append_files([otherdata1, otherdata2])
    HDF Appending: otherdata1.CDF
    HDF Appending: otherdata2.CDF

You can see a list of the files that are stored in this file by viewing the
``files`` attribute, which is a Pandas DataFrame. 

.. code::

    In : h5.files
              name         filename
    0  datasample1  datasample1.CDF
    1  otherdata1   otherdata1.CDF
    2  otherdata2   otherdata2.CDF

There are two name columns in this table: "name" and "filename". The latter is
the full file name as given when the GcmsFile object was created. This may
also contain path information to that file. Keep in mind that the path
information may not be correct if you've moved the location of this storage
file. In order to efficiently store the data on disk, the "filename" is
internally simplified the "name". This simplification removes the path and
suffix from "filename", and it replaces all ".", "-", and spaces with "_". In
addition, if "filename" starts with a number, the prefix "num" is added to
"name". If you have two or more "filenames" that simplify to the same "name",
you will run into problems. However, if you're file naming system does not
produce unique filenames for different data sets, you will most certainly have
more problems than just using these programs. 

You can extract data from the storage file using the ``extract_gcms_data``
method. This function takes one argument which is the name of the dataset that
you want to extract. This name can be either the simplified name or the
filename (with or without the path). The extracted data is the same file
object type as you stored originally. 

.. code:: 

    In : extracted = h5.extract_gcms_data('datasample1')

    In : extratced.filetype
    Out: "AiaFile"

Several other tables are added to this file when you run data calibration,
which is outlined in the next section.


.. _HDF file: http://www.hdfgroup.org/HDF5/
.. _PyTables: http://www.pytables.org/moin 
.. _Pandas: http://pandas.pydata.org/
