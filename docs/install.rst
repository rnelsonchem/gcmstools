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

The most convenient installation method for third-party Python packages is the
all-in-one `Anaconda Python distribution`_. It combines a large number of
Python packages for scientific data analysis and a program (``conda``) for
managing package updates, in addition to many other advanced features. The
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

There are three installation options for *gcmstools*: 1) install using conda
(recommended), 2) install using ``pip``, or 3) install the most recent
development version using ``git``.

*Option 1 (recommended)*

If you are using the Anaconda Python distribution, you can use ``conda`` to
install the most recent distribution of *gcmstools* from `Binstar`_,
Continuum's package repository.

.. code:: 

    home>$ conda install -c https://conda.binstar.org/rnelsonchem gcmstools

To uninstall *gcmstools* from a ``conda`` environment, use the following
command::

    home>$ conda remove gcmstools

*Option 2*

*gcmstools* can also be installed from the official Python packaging site,
`PyPI`_, using the standard Python installer script ``pip``. This installation
method will work fine if you have the additional dependencies installed;
otherwise, you may have some problems depending on your platform.

.. code:: 

    home>$ pip install gcmstools

To uninstall *gcmstools* using ``pip``::

    home>$ pip uninstall gcmstools


*Option 3*

The development version of *gcmstools* is hosted on `GitHub`_. To use this
version, you must install the `version-control software Git`_. *gcmstools* can
then be downloaded and installed with one ``pip`` command.

.. code::

    home>$ pip install git+https://github.com/rnelsonchem/gcmstools.git

There are advantages and disadvantages with this approach. For example, the
GitHub repo will always have the most recent updates and bug fixes; however,
these new features might not be as well-tested so you might find new bugs.

To uninstall, use the method described in *Option 2*

.. _GitHub: https://github.com/rnelsonchem/gcmstools
.. _version-control software Git: http://git-scm.com/
.. _Binstar: https://binstar.org/rnelsonchem
.. _PyPI: https://pypi.python.org/pypi/gcmstools


