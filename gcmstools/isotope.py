import numpy as np
import pandas as pd

from gcmstools.datastore import GcmsStore

class Isotope(object):
    '''An isotope analysis class.

    Parameters
    ----------
    h5file : str or GcmsStore instance
        This is the HDF file that contains all the processed data.

    datafile : str
        The file name for the data to be processed.

    name : str
        The name to give to this particular analysis.

    start : float
        The starting elution time for the analysis.

    stop : float (Default None)
        The ending elution time for the analysis. If `None`, then only a
        single MS slice at the indicated start time above will be used.
        Otherwise, all MS between the start and stop time will be averaged.

    rmbkg : bool (default False)
        Do a simple background removal of the analysis region. This simply
        subtracts the first MS slice from all the other MS data in the
        analysis region.
    '''
    def __init__(self, h5file, datafile, name, start, stop=None, rmbkg=False):
        if isinstance(h5file, str):
            self.h5 = GcmsStore(h5file)
        else:
            self.h5 = h5file

        self.data = self.h5.extract_gcms(datafile)
        self.name = name
        self.datafile = datafile
        
        self.start = start
        self.stop = stop
        self.rmbkg = rmbkg

        self.refs = {}
        
        self.datams = self._ms_select(self.data)
        self._dmask = np.zeros(self.data.masses.size, dtype=bool)


    def addref(self, reffile, refname, refmin, refmax, numiso, basemz,
            startmz=None):
        '''Add a reference spectrum.

        Parameters
        ----------
        reffile : str
            Reference file name.

        refname : str
            Name of reference compound.

        refmin : int
            The minimum m/z to select as a reference from this file.

        refmax : int
            The maximum m/z to select as a reference from this file.

        numiso : int
            The number of isotopologues to try and fit with this particular
            reference.

        basemz : int
            The starting m/z value that this reference will be used to fit.
            This can be different than refmin, especially if a true reference
            is contaminated.

        startmz : int (default None)
            The starting m/z value to fit this particular reference. This can
            only be equal to or larger than basemz. It may be necessary to
            make this larger if the first m/z value is contaminated with other
            compounds.
        '''
        if not startmz:
            startmz = basemz
        elif startmz < basemz:
            err = 'Staring m/z value must be greater than base m/z.'
            raise ValueError(err)

        gcms = self.h5.extract_gcms(reffile)

        # Get the MS and select only the region of interest
        refms = self._ms_select(gcms)
        mask = (gcms.masses >= refmin)
        mask = np.logical_and(gcms.masses <= refmax, mask)
        refvals = refms[mask]

        # Modify the data mask.  End m/z also needs also take into account the
        # number of masses for the reference, i.e. len(ref['vals'])
        endmz = startmz + numiso + (refmax - refmin)
        refmask = (self.data.masses >= startmz)
        refmask = np.logical_and(self.data.masses < endmz, refmask)
        self._dmask = np.logical_or(self._dmask, refmask)

        # Store all these values in the reference dictionary
        self.refs[refname] = {}
        tmpd = self.refs[refname]
        tmpd['file'] = reffile
        tmpd['refmin'] = refmin
        tmpd['refmax'] = refmax
        tmpd['basemz'] = basemz
        tmpd['numiso'] = numiso
        tmpd['startmz'] = startmz
        tmpd['vals'] = refvals
        #tmpd['gcms'] = gcms ###
        #tmpd['refms'] = refms ####
        #tmpd['refvals'] = refvals ####
        #tmpd['mask'] = mask ###
        #tmpd['ms'] = refms ####
       
    def fit(self, ):
        '''Fit the data using the reference information provided.'''
        # Get the MS intensities from the data for the region covered by the
        # references
        # MS intensities
        self.vals = self.datams[self._dmask]
        # Masses for the intensities
        self.masses = self.data.masses[self._dmask]

        # Create a DataFrame representation of the isotopolgue matrix
        self.isomat = self._iso_matrix_prep()

        # Perfom least squares fit
        # TODO: I should probably check some of the other vals besides coefs
        self._allfit = np.linalg.lstsq(self.isomat.T, self.vals)

        # Make a results DataFrame w/ same index as iso matrix, Coef column
        self.results = pd.DataFrame(self._allfit[0], index=self.isomat.index,
                columns=['Coef',])
        # As percents, needs to be done per compound (index level=0)
        self.results['Per'] = 0.0
        for cpd in self.results.index.levels[0]:
            df = self.results.ix[cpd]
            df['Per'] = df['Coef']*100./df['Coef'].sum()

        # Create a DataFrame of simulated and real MS with residuals
        siminten = self.isomat.mul(self.results['Coef'], axis=0)
        simdf = pd.DataFrame({'Real': self.vals, 
                'Sim Total': siminten.sum(axis=0)})
        simdf['Resid'] = simdf['Real'] - simdf['Sim Total']
        # Add the simulation per compound as well
        for cpd in siminten.index.levels[0]:
            df = siminten.ix[cpd]
            simdf[cpd + ' Sim'] = df.sum(axis=0)
        simdf.index.set_names('Mass', inplace=True)
        self.simdf = simdf

    def save(self, ):
        if not hasattr(self.h5.root, 'isotope'):
            self.h5._handle.create_group('/', 'isotope',
                    filters=self.h5._filters)
        isogrp = self.h5.root.isotope 

        if not hasattr(isogrp, self.data.shortname):
            self.h5._handle.create_group(isogrp, self.data.shortname,
                    filters=self.h5._filters)
        datagrp = getattr(isogrp, self.data.shortname)

        if hasattr(datagrp, self.name):
            self.h5._handle.remove_node(datagrp, self.name, recursive=True)
        grp = self.h5._handle.create_group(datagrp, self.name,
                filters=self.h5._filters)

        for k, v in self.__dict__.items():
            if isinstance(v, np.ndarray):
                self.h5._handle.create_carray(grp, k, obj=v)
            elif isinstance(v, pd.DataFrame):
                loc = grp._v_pathname
                self.h5.append(loc + '/' + k, v)
            elif isinstance(v, (str, list, dict, tuple, int, float)):
                self.h5._handle.set_node_attr(grp, k, v)
        

    def _ms_select(self, gcms):
        '''Select the MS from a data set'''
        if not self.stop:
            # Just grab a single slice
            idx = gcms.index(gcms.times, self.start)
            ms = gcms.intensity[idx]
            return ms/ms.max()
        else:
            # Select a range of MS spectra
            mask = (gcms.times > self.start) & (gcms.times < self.stop)
            region = gcms.intensity[mask]
            if self.rmbkg:
                # Subtract the first MS
                region = region - region[0]
            # Sum and normalize
            ms = region.sum(axis=0)
            return ms/ms.max()

    def _iso_matrix_prep(self, ):
        '''Create the isotopic matrix used for fitting.'''
        dfs = {}
        for refname in self.refs:
            ref = self.refs[refname]
            smz = ref['startmz']
            num = ref['numiso']
            base = ref['basemz']
            diff = smz - base
            rsz = ref['vals'].size
            isos = np.arange(diff, num+diff)
            zmat = np.zeros((num, self.vals.size))

            # This is making our "diagonal" matrix of masses
            for n in range(num):
                firstmz = smz+n
                lastmz = firstmz + rsz
                rng = np.where((self.masses >= firstmz) & \
                        (self.masses < lastmz)
                        )[0]
                rngsz = rng.size

                if rngsz >= rsz:
                    zmat[n, rng] = ref['vals']
                elif rngsz > 0:
                    zmat[n, rng] = ref['vals'][:rngsz]

            # Create a dataframe with this matrix, which is easier to concat
            tmpdf = pd.DataFrame(zmat, columns=self.masses, index=isos)
            dfs[refname] = tmpdf

        df = pd.concat(dfs)
        df.index.set_names(['Ref', 'Dnum'], inplace=True)
        return df

        
