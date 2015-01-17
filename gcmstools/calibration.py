import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tables as tb
import scipy.stats as sps

from gcmstools.datastore import HDFStore


class Calibrate(object):
    tblcols = ['Name', 'Start', 'Stop', 'Slope', 'Intercept', 'r', 'p',
            'stderr']

    def __init__(self, h5name, calfile):
        self.h5 = HDFStore(h5name)

        self.caldf = pd.read_csv(calfile)
        gb = self.caldf.groupby('Compound')
        all_calibration_data = []
        for group in gb:
            cal = self._proc_group(group)
            all_calibration_data.append(cal)
        self.h5.pdh5['calibration'] = pd.DataFrame(all_calibration_data,
                columns=Calibrate.tblcols)

        self.h5.pdh5.flush()

    def _proc_group(self, group):
        name, df = group

        fig = plt.figure()
        ax = fig.add_subplot(111)
        integrals = []
        for idx, series in df.iterrows():
            filename = series['File']
            gcms = self.h5.extract_gcms_data(filename)
            integrals.append(gcms.int_extract(name, series))
            nameidx = gcms.ref_cpds.index(name)
            ax.plot(gcms.times, gcms.int_sim[:,nameidx])
        
        ax.set_xlim(series['Start'], series['Stop'])
        fig.savefig(os.path.join('cal', name + '_fits'), dpi=200)
        fig.clear()

        conc = df['Concentration']
        integrals = np.array(integrals)

        std = series['Standard']
        has_std = isinstance(std, str) and not std.isspace()
        if has_std:
            stdconc = df['Standard Conc']
            conc = conc/stdconc

        slope, intercept, r, p, stderr = sps.linregress(conc, integrals)
        self._cal_plot(name, integrals, conc, slope, intercept, r)

        caldata = [name, series['Start'], series['Stop'], slope, intercept, r,
                p, stderr]

        return caldata

    def _cal_plot(self, name, integrals, conc, slope, intercept, r):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(conc, slope*conc + intercept, 'k-')
        ax.plot(conc, integrals, 'o', ms=8)
        text_string = 'Slope: {:.2f}\nIntercept: {:.2f}\nR^2: {:.5f}'
        ax.text(0.5, integrals.max()*0.8, text_string.format(slope, intercept, r**2))
        fig.savefig(os.path.join('cal', name+'_cal_curve'), dpi=200)
        fig.clear()

    def close():
        self.h5.close()

