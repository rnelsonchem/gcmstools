import re
from codecs import open

import numpy as np

class ReferenceFileGeneric(object):
    '''Generic object that defines refernce file methods.
    
    Requires subclass objects that have a _ref_file_proc method that processes
    a file called _ref_file.
    '''
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
        self.ref_array = []
        self.ref_files = []
        self.ref_meta = {}

        self._ref_file_proc(encoding)
        
        if bkg == True:
            bkg_idx = np.abs(self.times - bkg_time).argmin()
            bkg = self.intensity[bkg_idx]/self.intensity[bkg_idx].max()
            self.ref_array.append( bkg )
            self.ref_files.append( 'Background' )
            self._bkg_idx = bkg_idx
        
        self.ref_array = np.array(self.ref_array)


class TxtReference(ReferenceFileGeneric):
    '''txt Reference File class.

    These functions process a ".txt" reference MS file.
    '''
    def _ref_file_proc(self, encoding):
        fname = self._ref_file
        f = open(fname)

        for line in f:
            if line[0] == '#': continue
            elif line.isspace(): continue

            sp = line.split(':')
            sp = [i.strip() for i in sp]
            
            if sp[0] == "NAME":
                name = sp[1]
                self.ref_files.append(name)
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

        ref = self._ref_extend(mass, inten)
        self.ref_array.append(ref)

        return None

class MslReference(ReferenceFileGeneric):
    '''msl Reference File class.

    These functions process a ".MSL" (mass spectral libray) reference MS file.
    '''
    def _ref_file_proc(self, encoding):
        fname = self._ref_file
        regex = r'\(\s*(\d*)\s*(\d*)\)'
        recomp = re.compile(regex)
        
        f = open(fname, encoding=encoding)

        for line in f:
            if line[0] == '#': continue
            elif 'NAME' in line:
                sp = line.split(':')
                name = sp[1].strip()
                self.ref_files.append(name)
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
            
