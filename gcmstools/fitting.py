import numpy as np
import scipy.optimize as spo

import gcmstools.filetypes as gcf

class Fit(object):
    def __call__(self, datafiles):
        if isinstance(datafiles, gcf.GcmsFile):
            self.fit(datafiles)

        elif isinstance(datafiles, (tuple, list)):
            for data in datafiles:
                self.fit(data)

class Nnls(Fit):
    '''A non-negative least squares fitting object.'''
    def __init__(self, rt_filter=False, rt_win=0.2, rt_adj=0., quiet=False,
            **kwargs):
        self.fit_type = 'Nnls'
        self._quiet = quiet
        self.rt_filter = rt_filter
        if rt_filter:
            self.rt_win = rt_win
            self.rt_adj = rt_adj

    def _integrate(self, data):
        # Make the fits array 3D -> [len(times), len(cpds), 1]
        # multiply by the ref_array -> [len(cpds), len(masses)]
        # fit_ms = [len(times), len(cpds), len(masses)]
        # This is a huge array, so we won't store it in the object
        fit_ms = data.fit_coef[:,:,np.newaxis]*data.ref_array

        # Generate simulated MS for each component
        # Sum along the 3d dimmension (masses)
        # sim = [len(times), len(cpds)]
        sim = fit_ms.sum(axis=2)
        data.fit_sim = sim.copy()
        
        # Run a cummulative sum along the time axis of the simulation to get a
        # total integral, the difference between any two points is relative
        # integrals
        # fit_csum -> [len(times, len(cpds)]
        fit_csum = np.cumsum(sim, axis=0)
        data.fit_csum = fit_csum.copy()

        # Find the integrals and add them to the metadata
        for name, meta in data.ref_meta.items():
            if "START" in meta:
                start, stop = float(meta["START"]), float(meta["STOP"])
                integral = data._int_extract(name, start, stop)
                data.ref_meta[name]["integral"] = integral

    def fit(self, data):
        if not hasattr(data, 'ref_array'):
            error = "The datafile {} does not have reference data."
            raise ValueError(error.format(data.filename))

        if not self._quiet:
            print("Fitting: {}".format(data.filename))

        fits = []
        ref_cpds = data.ref_cpds
        times = data.times
        inten = data.intensity
        ref_meta = data.ref_meta 
        ref_array = data.ref_array
        
        # If a retention time filter is requested, then build up an array of
        # retention times from the meta data
        if self.rt_filter == True:
            ret_times = self._rt_filter_times(ref_cpds, ref_meta)

        for time, ms in zip(times, inten):
            if self.rt_filter == False:
                # If no retention time filter, just do standard fit
                fit, junk = spo.nnls(ref_array.T, ms)
            else:
                # Or else to a special retention time filtered fit
                fit = self._rt_filter_fit(ret_times, time, ms, ref_array,
                        ref_cpds)

            fits.append( fit )
        
        data.fit_type = self.fit_type
        data.fit_coef = np.array( fits )
        self._integrate(data)

    def _rt_filter_times(self, ref_cpds, ref_meta):
        '''Collect a list of retention times from metadata.'''
        rts = []
        for name in ref_cpds:
            if name == 'Background':
                rts.append( -5. )
                continue
            rt = ref_meta[name]['RT']
            rts.append(rt)
        ret_times = np.array(rts, dtype=float)
        return ret_times

    def _rt_filter_fit(self, ret_times, time, ms, ref_array, ref_cpds):
        '''Fit only compounds that are within a certain retention window.'''
        # Create a boolean RT filter mask
        mask = ((ret_times + self.rt_adj) > (time - self.rt_win)) & \
                ((ret_times + self.rt_adj) < (time + self.rt_win))
        zeros = np.zeros( len(ref_cpds) )
        # Check if the filter has any hits
        msum = mask.sum()
        if msum != 0:
            if ref_cpds[-1] == 'Background':
                mask[-1] = True
            ref_arr_mask = ref_array[mask]
            fit, junk = spo.nnls(ref_arr_mask.T, ms)
            zeros[mask] = fit
            fit = zeros
        # If no RT hits, fit the data with either the background or
        # use only zeros
        else:
            if self.ref_cpds[-1] == 'Background':
                fit, junk = spo.nnls(ref_array[-1].reshape(-1,1),
                        ms)
                zeros[-1] = fit[0]
            fit = zeros
        return fit
