.. _install:

Installation
############

*Gcmstools* requires Python and a number of third-party packages. Below is a
complete list of packages and minium versions:

* Python >=3.4 (2.x versions not supported any longer)
* Pip >=6.0.6 (might be part of newer Python releases)
* Setuptools >=11.3.1 
* Numpy >=1.9.1 
* Matplotlib >= 1.4.2
* Pandas >=0.15.2
* IPython >=2.3.1
* PyTables >=3.1.1
* Scipy >=0.14.0
* Sphinx >=1.2.2 (Optional for documentation.)

  * numfig is a Sphinx extenstion that is needed to autonumber figures
    references in the docuementation.

IPython is also a very useful advanced interactive Python interpreter.
Examples in this documentation assume that you are using this environment.
See the :ref:`ipython` section of :doc:`Appendix A <appendA>` for more
details.

Python
------

The most convenient installation method for Python other third-party packages
is the all-in-one `Anaconda Python distribution`_. It combines a large number
of Python packages for scientific data analysis and a program (``conda``) for
managing package updates (in addition to many other advanced features). The
Anaconda developers (Continuum Analytics) provide a lot of useful
documentation on `installing Anaconda`_ and `using conda`_. There are other
ways to install Python and the third-party packages, but for this
documentation, it will be assumed that your are using Anaconda.

.. note::

    On Mac/Linux, Python is already part of the operating system.  Do not try
    to install these third-party packages into the builtin Python distribution
    unless you really know what you are doing. You might overwrite an
    important file, which can cause problems for your system.  Confusion
    between the system and Anaconda Python installation is a common source of
    problems for beginners, so make sure that your Anaconda Python is
    "activated" before running the commands in this document. (See the
    Anaconda documentation for more information on the activation process.)
    
Learning the usage of all of these Python packages is far beyond the scope of
this document. However, excellent documentation for most of the packages as
well as full tutorials are `easily discovered`_.

.. _Anaconda Python distribution: http://continuum.io/downloads
.. _installing Anaconda: http://docs.continuum.io/anaconda/
.. _using conda: http://conda.pydata.org/docs/
.. _Christoph Gohlke: http://www.lfd.uci.edu/~gohlke/pythonlibs/
.. _easily discovered: https://google.com

gcmstools
---------

There are two installation options for *gcmstools*: 1) install using ``git``
(recommended) or 2) download the source file and install the package. 

*Option 1 (recommended)*

First, install the `version-control software Git`_. *gcmstools* can now be
downloaded and installed with one command.

.. code::

    home>$ pip install git+https://github.com/rnelsonchem/gcmstools.git

The advantage here is that the same command will update your *gcmstools*
installation with any any changes that have been made to `the main
repository`_. 

*Option 2*

Download a zip file of the current state of the repository. (Look for the
button shown below (:num:`Figure #gitzip`) at `the main repository`_.) Unzip
this package wherever you'd like.

.. _gitzip:

.. figure:: ./_static/images/git_zip.png
    
    The zipfile download button.

From the command line, navigate the newly extracted folder and use ``pip`` to
install the package.  In this case, *path-to-gcmstools-folder* is the location
of the newly unzipped *gcmstools* folder. Be sure to put a dot (``.``) at the
end of that pip command.

.. code::

    home>$ cd path-to-gcmstools-folder
    gcmstools>$ pip install .

*Uninstall*

Uninstallation of *gcmstools* is trivial. It may be a good idea to run this
command before installing updates as well to ensure that the most recent
version of *gmcstools* is being installed.

.. code::

    home>$ pip uninstall gcmstools

.. _the main repository: https://github.com/rnelsonchem/gcmstools
.. _version-control software Git: http://git-scm.com/


