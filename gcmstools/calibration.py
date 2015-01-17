import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tables as tb
import scipy.stats as sps

from gcmstools.datastore import HDFStore


class Calibrate(object):
    tblcols = ['Name', 'Start', 'Stop', 'Slope', 'Intercept', 'r', 'p',
            'stderr']

    def __init__(self, h5name, calfile, calfolder='cal', clear_folder=True,
            quiet=False, **kwargs):
        self._quiet = quiet
        self.h5 = HDFStore(h5name)

        self.calfolder = calfolder
        if os.path.isdir(calfolder) and clear_folder:
            shutil.rmtree(calfolder)
            os.mkdir(calfolder)
        elif not os.path.isdir(calfolder):
            os.mkdir(calfolder)

        self.calinput = pd.read_csv(calfile)
        gb = self.calinput.groupby('Compound')
        all_calibration_data = []
        for group in gb:
            cal = self._proc_group(group)
            all_calibration_data.append(cal)

        self.h5.pdh5['calibration'] = pd.DataFrame(all_calibration_data)\
                .set_index('Compound')
        self.calibration = self.h5.pdh5['calibration']
        self.h5.pdh5['calinput'] = self.calinput
        self.h5.pdh5.flush()
        
        mask = self.h5.pdh5.files['filename'].isin(self.h5.pdh5.calinput['File']) 
        others_df = self.h5.pdh5.files[~mask]
        dicts = {}
        for idx, line in others_df.iterrows():
            datadict = self._data_proc(line)
            dicts[line['filename']] = datadict
        df = pd.DataFrame(dicts).T
        df.index.name = 'name'
        self.h5.pdh5['datacal'] = df
        self.h5.pdh5.flush()
            
    def _data_proc(self, line):
        if not self._quiet:
            print("Processing: {}".format(line['filename']))

        gcms = self.h5.extract_gcms_data(line['filename']) 
        data = {}
        for name, series in self.calibration.iterrows():
            integral = gcms.int_extract(name, series)
            data[name] = (integral - series['intercept'])/series['slope']

        return data

    def _proc_group(self, group):
        name, df = group
        if not self._quiet:
            print("Calibrating: {}".format(name))

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
        fig.savefig(os.path.join(self.calfolder, name + '_fits'), dpi=200)
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

        series.pop('File')
        series.pop('Concentration')
        series.pop('Standard Conc')
        series['slope'] = slope
        series['intercept'] = intercept
        series['r'] = r
        series['p'] = p
        series['stderr'] = stderr
        return series

    def _cal_plot(self, name, integrals, conc, slope, intercept, r):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(conc, slope*conc + intercept, 'k-')
        ax.plot(conc, integrals, 'o', ms=8)
        text_string = 'Slope: {:.2f}\nIntercept: {:.2f}\nR^2: {:.5f}'
        ax.text(0.5, integrals.max()*0.8, text_string.format(slope, intercept, r**2))
        fig.savefig(os.path.join(self.calfolder, name+'_cal_curve'), dpi=200)
        fig.clear()

    def close(self,):
        self.h5.close()

