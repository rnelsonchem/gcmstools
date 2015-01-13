import re
from codecs import open

import numpy as np

import filetypes as gcf

class ReferenceFileGeneric(object):
    '''Generic object that defines refernce file methods.
    
    Requires subclass objects that have a _ref_file_proc method that processes
    a file called ref_file.
    '''
    def __init__(self, ref_file, bkg=True, bkg_time=0., encoding='ascii'):
        self.ref_file = ref_file
        self.bkg = bkg
        self.bkg_time = bkg_time
        self.encoding = encoding

        self.ref_build()

    def __call__(self, datafiles):
        if isinstance(datafiles, gcf.GcmsFile):
            self.data = datafiles
            self._append_ref_array()

        elif isinstance(datafiles, (tuple, list)):
            for data in datafiles:
                self.data = data
                self._append_ref_array()

        del(self.data)

    def _append_ref_array(self, ):
        ref_array = []
        data_min = self.data.masses.min()
        data_max = self.data.masses.max()
        spec = np.empty(self.data.masses.size, dtype=float)
        
        for mass, inten in self.ref_mass_inten:
            spec[:] = 0.
            mask = (mass > data_min) & (mass < data_max)
            mass_mask = mass[mask] - data_min
            inten_mask = inten[mask]

            spec[mass_mask] = inten
            ref_array.append( spec/spec.max() )

        if self.bkg == True:
            times = self.data.times
            inten = self.data.intensity
            bkg_idx = np.abs(times - self.bkg_time).argmin()
            bkg = inten[bkg_idx]/inten[bkg_idx].max()
            ref_array.append( bkg )

            bkg_dict = {'bkg_time': self.bkg_time,
                    'bkg_idx': bkg_idx, 
                    }
            self.ref_meta['Background'] = bkg_dict

        if (self.bkg == False) and ('Background' in self.ref_meta):
            self.ref_meta.pop('Background')
        
        self.data.ref_array = np.array(ref_array)
        self.data.ref_meta = self.ref_meta
        self.data.ref_cpds = self.ref_cpds
        
    def _ref_extend(self, masses, intensities):
        masses = np.array(masses, dtype=int)
        intensities = np.array(intensities, dtype=float)
        mask = (masses > self.masses.min()) & (masses < self.masses.max())
        masses = masses[mask] - self.masses.min()
        intensities = intensities[mask]

        spec = np.zeros(self.masses.size, dtype=float)
        spec[masses] = intensities
        return spec/spec.max()

    def ref_build(self, bkg=True, bkg_time=0., encoding='ascii'):
        self.ref_mass_inten = []
        self.ref_cpds = []
        self.ref_meta = {}

        self._ref_file_proc()
        
        if self.bkg == True:
            self.ref_cpds.append( 'Background' )


class TxtReference(ReferenceFileGeneric):
    '''txt Reference File class.

    These functions process a ".txt" reference MS file.
    '''
    def _ref_file_proc(self, ):
        fname = self.ref_file
        f = open(fname)

        for line in f:
            if line[0] == '#': continue
            elif line.isspace(): continue

            sp = line.split(':')
            sp = [i.strip() for i in sp]
            
            if sp[0] == "NAME":
                name = sp[1]
                self.ref_cpds.append(name)
                self.ref_meta[name] = {}
            elif sp[0] == "NUM PEAKS":
                line = self._ref_entry_proc(f, name=name)
                if line:
                    sp = line.split(":")
                    sp = [i.strip() for i in sp]
                    self.ref_meta[name][sp[0]] = sp[1]
            else:
                self.ref_meta[name][sp[0]] = sp[1]

    def _ref_entry_proc(self, fobj, name):
        inten = []
        mass = []

        for line in fobj:
            if line[0] == '#': continue
            elif line.isspace(): break
            elif ":" in line: 
                return line

            vals = line.split()
            mass.append(vals[0])
            inten.append(vals[1])

#        ref = self._ref_extend(mass, inten)
#        self.ref_array.append(ref)
        mass = np.array(mass, dtype=int)
        inten = np.array(inten, dtype=float)
        self.ref_mass_inten.append((mass, inten))

        return None

class MslReference(ReferenceFileGeneric):
    '''msl Reference File class.

    These functions process a ".MSL" (mass spectral libray) reference MS file.
    '''
    def _ref_file_proc(self, ):
        fname = self.ref_file
        regex = r'\(\s*(\d*)\s*(\d*)\)'
        recomp = re.compile(regex)
        
        f = open(fname, encoding=encoding)

        for line in f:
            if line[0] == '#': continue
            elif 'NAME' in line:
                sp = line.split(':')
                name = sp[1].strip()
                self.ref_cpds.append(name)
                self.ref_meta[name] = {}
                self._msl_ref(f, name=name, recomp=recomp)


    def _ref_entry_proc(self, fobj, name, recomp):
        for line in fobj:
            if line[0] == '#': continue
            space = line.isspace()

            if 'NUM PEAK' in line:
                inten = []
                mass = []
                for line in fobj:
                    if line.isspace():
                        space = True
                        break
                    vals = recomp.findall(line)
                    for val in vals:
                        mass.append(val[0])
                        inten.append(val[1])
                ref = self._ref_extend(mass, inten)
                self.ref_array.append(ref)
                if space:
                    return None

            elif not space:
                meta = line.split(':')
                self.ref_meta[name][meta[0]] = meta[1].strip()

            if space:
                return None
            
