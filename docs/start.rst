Getting started
###############

*gcmstools* is a Python package that reads some GCMS file formats and does
simple fitting. The source code for this project can be found on `GitHub`_. If
you are reading this in PDF format, there is `online documentation`_ as well.

This user guide is broken into a few sections. 

#. :ref:`Installation <install>`: Information about getting a Python
   installation up and running and installing *gcmstools*.

#. :ref:`Basic Usage <basics>`: This section covers the usage of *gcmstools*
   to manipulate and plot GCMS data. 

#. Referencing: Incorporate reference data along with the GCMS data set.

#. :ref:`Fitting <fit>`: Manually fit the GCMS data set using the reference
   information.
   
#. :ref:`Calibration <cal>`: Make a calibration file and use this to extract
   generate concentration information from your data. 

#. :ref:`Batch Processing <batch>`: Covers a simple function for automating
   this entire process. You can skip to this final sections if all you want to
   do is automate some data extractions. It is not necessary to understand the
   basics of data manipulation/plotting.

.. note::
    
    The examples presented in this document require a basic working knowledge
    of a command-line terminal interface and running Python commands from an
    interpreter. :ref:`Appendix A <cli>` covers the basics that you will need
    to run these examples.

.. _GitHub: https://github.com/rnelsonchem/gcmstools
.. _online documentation: http://gcmstools.rcnelson.com/

