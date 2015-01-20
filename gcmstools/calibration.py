import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tables as tb
import scipy.stats as sps

from gcmstools.datastore import HDFStore


class Calibrate(object):
    def __init__(self, h5name='data.h5', clear_folder=True, quiet=False,
            dpi=100, **kwargs):
        self._quiet = quiet
        self._clear_folder = clear_folder
        self._dpi = dpi

        if isinstance(h5name, str):
            self.h5 = HDFStore(h5name)
        else:
            self.h5 = h5name
        
    def curvegen(self, calfile, calfolder='cal', picts=False, **kwargs):
        self.calfolder = calfolder
        self.calfile = calfile
        self._calpicts = picts

        if picts:
            if os.path.isdir(self.calfolder) and self._clear_folder:
                shutil.rmtree(self.calfolder)
                os.mkdir(self.calfolder)
            elif not os.path.isdir(self.calfolder):
                os.mkdir(self.calfolder)

        self.calinput = pd.read_csv(self.calfile, comment='#')
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

        if picts:
            for i in self.calibration.index:
                self.curveplot(i, folder=calfolder)

    def _cal_group_proc(self, group):
        name, df = group
        if not self._quiet:
            print("Calibrating: {}".format(name))

        integrals = []
        for idx, series in df.iterrows():
            filename = series['File']
            gcms = self.h5.extract_data(filename)
            integrals.append(gcms._int_extract(name, series))

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

        series.pop('File')
        series.pop('Concentration')
        series.pop('Standard Conc')
        series['slope'] = slope
        series['intercept'] = intercept
        series['r'] = r
        series['p'] = p
        series['stderr'] = stderr
        return series

    def fitsplot(self, cpd, calfolder='cal', show=False, save=True, **kwargs):
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
            gcms = self.h5.extract_data(row['File'])
            nameidx = gcms.ref_cpds.index(cpd)
            ax.plot(gcms.times, gcms.fit_sim[:,nameidx])
        
        ax.set_xlim(row['Start'], row['Stop'])
        if save:
            fig.savefig(os.path.join(calfolder, cpd + '_fits'),
                    dpi=self._dpi)
        if show:
            plt.show()
        plt.close(fig)

    def curveplot(self, name, folder='.', show=False, save=True):
        if not hasattr(self, 'calinput'):
            try:
                self.calinput = self.h5.pdh5.calinput
            except:
                print("No calibration DataFrame!")
                return

        s = self.h5.pdh5.calibration.loc[name]
        mask = self.calinput['Compound'] == name
        df = self.calinput[mask]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(df.conc, s.slope*df.conc + s.intercept, 'k-')
        ax.plot(df.conc, df.integral, 'o', ms=8)
        text_string = 'Slope: {:.2f}\nIntercept: {:.2f}\nR^2: {:.5f}'
        ax.text(0.5, df.integral.max()*0.8, text_string.format(s.slope, 
            s.intercept, s.r**2))
        if save:
            fig.savefig(os.path.join(folder, name+'_cal_curve'), 
                    dpi=self._dpi)
        if show:
            plt.show()
        plt.close(fig)
            
    def datagen(self, datafolder='proc', picts=False, **kwargs):
        self.datafolder = datafolder
        self._datapicts = picts
        if not hasattr(self, 'calibration'):
            try:
                self.calibration = self.h5.pdh5.calibration
            except:
                print("No calibration DataFrame!")
                return

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
            gcms = self.h5.extract_data(line['filename']) 
            datadict = self._data_group_proc((line, gcms))
            dicts[line['name']] = datadict

        df = pd.DataFrame(dicts).T
        df.index.name = 'name'
        self.h5.pdh5['datacal'] = df
        self.datacal = self.h5.pdh5.datacal
        self.h5.pdh5.flush()

    def _data_group_proc(self, linegcms):
        line, gcms = linegcms
        data = {}
        for name, series in self.calibration.iterrows():
            integral = gcms._int_extract(name, series)
            conc = (integral - series['intercept'])/series['slope']
            data[name] = conc
            if self._datapicts:
                self.dataplot(name, gcms, conc, folder=self.datafolder)
        return data

    def dataplot(self, name, gcmsfile, conc=None, folder='.', show=False,
            save=True):
        if isinstance(gcmsfile, str):
            gcms = self.h5.extract_data(gcmsfile)
        else:
            gcms = gcmsfile

        if not conc:
            conc = self.h5.pdh5.datacal.loc[gcmsfile, name]

        s = self.h5.pdh5.calibration.loc[name]
        cpdidx = gcms.ref_cpds.index(name)
        sim = gcms.fit_sim[:,cpdidx]

        start, stop = s.Start, s.Stop
        mask = (gcms.times > start) & (gcms.times < stop)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(gcms.times[mask], sim[mask])
        ax.plot(gcms.times[mask], gcms.tic[mask], 'k', lw=1.5)
        ax.set_title('Concentration = {:.2f}'.format(conc))
        if save:
            fig.savefig(os.path.join(folder, gcms.shortname + '_' + name + '.png'),
                    dpi=self._dpi)
        if show:
            plt.show()
        plt.close(fig)

    def close(self,):
        self.h5.close()

