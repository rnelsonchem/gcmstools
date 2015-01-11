import numpy as np
import scipy.optimize as spo

class Fit(object):
    pass

class Nnls(Fit):
    '''A non-negative least squares fitting object.'''
    def nnls(self, rt_filter=False, rt_win=0.2, rt_adj=0.):
        fits = []
        
        # If a retention time filter is requested, then build up an array of
        # retention times from the meta data
        if rt_filter == True:
            rts = []
            for name in self.ref_files:
                if name == 'Background':
                    rts.append( -5. )
                    continue
                rt = self.ref_meta[name]['RT']
                rts.append(rt)
            self.ret_times = np.array(rts, dtype=float)

        for time, ms in zip(self.times, self.intensity):
            # If no retention time filter, just do standard fit
            if rt_filter == False:
                fit, junk = spo.nnls(self.ref_array.T, ms)

            else:
                # Create a boolean RT filter mask
                mask = ((self.ret_times + rt_adj) > (time - rt_win)) & \
                        ((self.ret_times + rt_adj) < (time + rt_win))
                zeros = np.zeros( len(self.ref_files) )
                # Check if the filter has any hits
                msum = mask.sum()
                if msum != 0:
                    if self.ref_files[-1] == 'Background':
                        mask[-1] = True
                    ref_arr = self.ref_array[mask]
                    fit, junk = spo.nnls(ref_arr.T, ms)
                    zeros[mask] = fit
                    fit = zeros
                # If no RT hits, fit the data with either the background or
                # use only zeros
                else:
                    if self.ref_files[-1] == 'Background':
                        fit, junk = spo.nnls(self.ref_array[-1].reshape(-1,1)
                                , ms)
                        zeros[-1] = fit[0]
                    fit = zeros

            fits.append( fit )

        self.fits = np.array( fits )


    def integrate(self, start, stop):
        mask = (self.times > start) & (self.times < stop)
        self.last_int_start = start
        self.last_int_stop = stop

        chunk = self.fits[mask]
        self.last_int_mask = mask
        self.last_int_fits = chunk

        fit_ms = chunk[:,:,np.newaxis]*self.ref_array
        self.last_int_ms = fit_ms

        sim = fit_ms.sum(axis=2)
        self.last_int_sim = sim
        
        integral = fit_ms.sum( axis = (0,2) )
        self.integral = integral


