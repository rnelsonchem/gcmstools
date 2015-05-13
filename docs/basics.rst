.. _basics:

Basic Setup
###########

Below are the instructions for setting up an environment that will let you
work through this documentation. 

The processing environment
--------------------------

In these examples, we will run *gcmstools* from a terminal IPython session in
a folder "gcms", which is located in your home directory. Basic information
about using the terminal and IPython is found in :doc:`appendA`.

.. code::

    home>$ cd gcms

    gcms>$ ipython
    Python 3.4.1 (default, Oct 10 2014, 15:29:52)
    Type "copyright", "credits" or "license" for more information.
    
    IPython 2.3.1 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.
    
    In : 

Sample Data
-----------

A :download:`zip archive containing example files <../sampledata.zip>` is
provided in the online *gcmstools* documentation. These files can be
downloaded into the current directory using the ``get_sample_data`` function.

.. code::

    In : from gcmstools.general import get_sample_data

    In : get_sample_data()

