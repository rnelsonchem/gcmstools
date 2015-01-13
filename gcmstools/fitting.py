import numpy as np
import scipy.optimize as spo

import filetypes as gcf

class Fit(object):
    def __call__(self, datafiles):
        if isinstance(datafiles, gcf.GcmsFile):
            self.data = datafiles
            self.fit()

        elif isinstance(datafiles, (tuple, list)):
            for data in datafiles:
                self.data = data
                self.fit()

    def integrate(self, datafiles, start, stop):
        if isinstance(datafiles, gcf.GcmsFile):
            self._integrate(datafiles, start, stop)

        elif isinstance(datafiles, (tuple, list)):
            for data in datafiles:
                self._integrate(data, start, stop)

class Nnls(Fit):
    '''A non-negative least squares fitting object.'''
    def __init__(self, rt_filter=False, rt_win=0.2, rt_adj=0.):
        self.rt_filter = rt_filter
        if rt_filter:
            self.rt_win = rt_win
            self.rt_adj = rt_adj

    def _integrate(self, data, start, stop):
        mask = (data.times > start) & (data.times < stop)
        data.int_start = start
        data.int_stop = stop
        data.int_mask = mask

        chunk = data.fits[mask]
        data.int_fits = chunk

        fit_ms = chunk[:,:,np.newaxis]*data.ref_array
        data.int_ms = fit_ms

        sim = fit_ms.sum(axis=2)
        data.int_sim = sim
        
        integral = fit_ms.sum( axis = (0,2) )
        data.integral = integral

    def fit(self, ):
        if not hasattr(self.data, 'ref_array'):
            error = "The datafile {} does not have reference data."
            raise ValueError(error.format(self.data.filename))

        fits = []
        ref_cpds = self.data.ref_cpds
        times = self.data.times
        inten = self.data.intensity
        ref_meta = self.data.ref_meta 
        ref_array = self.data.ref_array
        
        # If a retention time filter is requested, then build up an array of
        # retention times from the meta data
        if self.rt_filter == True:
            ret_times = self._rt_filter_times(ref_cpds, ref_meta)

        for time, ms in zip(times, inten):
            # If no retention time filter, just do standard fit
            if self.rt_filter == False:
                fit, junk = spo.nnls(ref_array.T, ms)
            # Or else to a special retention time filtered fit
            else:
                fit = self._rt_filter_fit(ret_times, time, ms, ref_array,
                        ref_cpds)

            fits.append( fit )

        self.data.fits = np.array( fits )

    def _rt_filter_times(self, ref_cpds, ref_meta):
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
