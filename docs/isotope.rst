Isotopic Distribution Analysis
##############################

When running reactions with isotopically labeled substrates, it may be
important to determine the distribution of the isotope labels in the resulting
product. The ``gcmstools.isotope`` module defines an ``Isotope`` class that is
meant to assist in this analysis. In short, this class helps you to build a
matrix of reference spectra which is used in a least squares fit with the
observed mass distribution. 

