import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tables as tb
import scipy.stats as sps

from gcmstools.datastore import HDFStore


class Calibrate(object):
    def __init__(self, h5name, clear_folder=True, quiet=False, dpi=100, 
            **kwargs):
        self._quiet = quiet
        self._clear_folder = clear_folder
        self._dpi = dpi

        if isinstance(h5name, str):
            self.h5 = HDFStore(h5name)
        else:
            self.h5 = h5name
        
    def curvegen(self, calfile, calfolder='cal', picts=True):
        self.calfolder = calfolder
        self.calfile = calfile
        self._calpicts = picts

        if picts:
            if os.path.isdir(self.calfolder) and self._clear_folder:
                shutil.rmtree(self.calfolder)
                os.mkdir(self.calfolder)
            elif not os.path.isdir(self.calfolder):
                os.mkdir(self.calfolder)

        self.calinput = pd.read_csv(self.calfile)
        gb = self.calinput.groupby('Compound')
        all_calibration_data = []
        for group in gb:
            cal = self._cal_group_proc(group)
            all_calibration_data.append(cal)

        self.h5.pdh5['calibration'] = pd.DataFrame(all_calibration_data)\
                .set_index('Compound')
        self.calibration = self.h5.pdh5['calibration']
        self.h5.pdh5['calinput'] = self.calinput
        self.h5.pdh5.flush()

    def _cal_group_proc(self, group):
        name, df = group
        if not self._quiet:
            print("Calibrating: {}".format(name))

        integrals = []
        for idx, series in df.iterrows():
            filename = series['File']
            gcms = self.h5.extract_gcms_data(filename)
            integrals.append(gcms.int_extract(name, series))

        conc = df['Concentration']
        integrals = np.array(integrals)

        std = series['Standard']
        has_std = isinstance(std, str) and not std.isspace()
        if has_std:
            stdconc = df['Standard Conc']
            conc = conc/stdconc
        
        mask = self.calinput['Compound'] == name
        self.calinput.loc[mask, 'conc'] = conc
        self.calinput.loc[mask, 'integral'] = integrals

        slope, intercept, r, p, stderr = sps.linregress(conc, integrals)
        if self._calpicts:
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

    def fitsplot(self, cpd, calfolder='.', show=False, save=True):
        if not hasattr(self, 'calinput'):
            try:
                self.calinput = self.h5.pdh5.calinput
            except:
                print("No calibration DataFrame!")
                return

        mask = self.calinput['Compound'] == cpd
        df = self.calinput[mask]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        for idx, row in df.iterrows():
            gcms = self.h5.extract_gcms_data(row['File'])
            nameidx = gcms.ref_cpds.index(cpd)
            ax.plot(gcms.times, gcms.int_sim[:,nameidx])
        
        ax.set_xlim(row['Start'], row['Stop'])
        if save:
            fig.savefig(os.path.join(calfolder, cpd + '_fits'),
                    dpi=self._dpi)
        if show:
            plt.show()
        plt.close(fig)

    def _cal_plot(self, name, integrals, conc, slope, intercept, r):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(conc, slope*conc + intercept, 'k-')
        ax.plot(conc, integrals, 'o', ms=8)
        text_string = 'Slope: {:.2f}\nIntercept: {:.2f}\nR^2: {:.5f}'
        ax.text(0.5, integrals.max()*0.8, text_string.format(slope, 
            intercept, r**2))
        fig.savefig(os.path.join(self.calfolder, name+'_cal_curve'), 
                dpi=self._dpi)
        plt.close(fig)
            
    def datagen(self, datafolder='proc', picts=True):
        self.datafolder = datafolder
        self._datapicts = picts

        if picts:
            if os.path.isdir(self.datafolder) and self._clear_folder:
                shutil.rmtree(self.datafolder)
                os.mkdir(self.datafolder)
            elif not os.path.isdir(self.datafolder):
                os.mkdir(self.datafolder)
        
        mask = self.h5.pdh5.files['filename'].isin(self.h5.pdh5.calinput['File'])
        others_df = self.h5.pdh5.files[~mask]
        dicts = {}

        for idx, line in others_df.iterrows():
            if not self._quiet:
                print("Processing: {}".format(line['filename']))
            gcms = self.h5.extract_gcms_data(line['filename']) 
            datadict = self._data_group_proc((line, gcms))
            dicts[line['filename']] = datadict

        df = pd.DataFrame(dicts).T
        df.index.name = 'name'
        self.h5.pdh5['datacal'] = df
        self.h5.pdh5.flush()

    def _data_group_proc(self, linegcms):
        line, gcms = linegcms
        data = {}
        for name, series in self.calibration.iterrows():
            integral = gcms.int_extract(name, series)
            conc = (integral - series['intercept'])/series['slope']
            data[name] = conc
            if self._datapicts:
                self._data_plot(name, gcms, conc, series, line)
        return data

    def _data_plot(self, name, gcms, conc, series, line):
        cpdidx = gcms.ref_cpds.index(name)
        sim = gcms.int_sim[:,cpdidx]

        start, stop = series['Start'], series['Stop']
        mask = (gcms.times > start) & (gcms.times < stop)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(gcms.times[mask], sim[mask])
        ax.plot(gcms.times[mask], gcms.tic[mask], 'k', lw=1.5)
        ax.set_title('Concentration = {:.2f}'.format(conc))
        fig.savefig(os.path.join(self.datafolder, 
                line['name'] + '_' + name + '.png'), dpi=self._dpi)
        plt.close(fig)

    def close(self,):
        self.h5.close()

