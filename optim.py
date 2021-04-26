import os
import numpy as np
from scipy.interpolate import interp1d

class Data(object):
    def __init__(self, time, val, position):

        self._n = len(time)
        self.time = np.zeros(self._n, float)
        self.val = np.zeros(self._n, float)
        self.positoin = np.zeros(self._n, float)

        self.time = np.array([float(i) for i in time])
        self.val = np.array([float(i) for i in val])
        self.position = np.array([int(i) for i in position])

class ObsData(object):
    def __init__(self, time, val, position):

        time = np.array([float(i) for i in time])
        val = np.array([float(i) for i in val])
        position = np.array([int(i) for i in position])
        self.mat = np.unique(position)

        self.data = []
        for imat in self.mat:
            which = imat == position
            self.data.append(Data(time[which], val[which], position[which]))
        
class ModData(object):
    def __init__(self, time, val, position):

        time = np.array([float(i) for i in time])
        val = np.array([float(i) for i in val])
        position = np.array([int(i) for i in position])
        self.mat = np.unique(position)

        self.data = []
        for imat in self.mat:
            which = imat == position
            self.data.append(Data(time[which], val[which], position[which]))
        


class Optim(object):
    
    def __init__(self,hydro_proj, outdir):
        self.hp = hydro_proj
        self.outdir = outdir
        self.exe = 'H1D_CALC.EXE'

        tmp = self.read_measured()
        self.obs = ObsData(tmp[0], tmp[1], tmp[2])
        self.mat = self.obs.mat

    def get_params(self):
        file_ = '{}/{}'.format(self.hp, 'SELECTOR.IN')
        with open(file_,'r') as f:
            lines = f.readlines()
        NMat = int(lines[13].split()[0])
        params = []
        for i in range(NMat):
            line = lines[26+i].split()
            params.append([float(i) for i in line])

        return params

    def set_params(self, params):
        """ Sets params in to SELECTOR.IN """

        file_ = '{}/{}'.format(self.hp, 'SELECTOR.IN')
        with open(file_,'r') as f:
            lines = f.readlines()
        NMat = int(lines[13].split()[0])

        # TODO
        #if not(len(params) == NMat): ERROR
        
        i = 0
        for p in params: # replace lines in selector 
            str_ = ' '.join([str(elem) for elem in p]) + '\n'
            lines[26+i] = str_
            i += 1

        with open(file_,'w') as f:
            f.writelines(lines)

    def read_modeled(self):
        file_ = '{}/{}'.format(self.hp, 'Obs_Node.out')
        with open(file_,'r') as f:
            lines = f.readlines()

        counter = 0
        for line in lines:
            if 'time' in line:
                start = counter
            if 'end' in line:
                end = counter
            counter += 1

        ctime = 0
        time = []
        val = []
        position = []
        for i in range(start+1, end):
            line = lines[i].split()
            for imat in self.mat:
                cval = imat*3-1
                time.append(line[ctime])
                val.append(line[cval])
                position.append(imat)

        return time, val, position

    def read_measured(self):
        file_ = '{}/{}'.format(self.hp, 'Fit.out')
        with open(file_,'r') as f:
            lines = f.readlines()

        counter = 0
        for line in lines:
            if 'Observed Quantity' in line:
                start = counter
            if 'Parameter estimation with' in line:
                end = counter
            counter += 1

        time = []
        val = []
        position = []
        for i in range(start+3, end-3):
            line = lines[i].split()
            time.append(line[1])
            val.append(line[2])
            position.append(line[4])

        return time, val, position

    def _interpolate(self, val, time, time2):
        f = interp1d(time, val)
        return f(time2)

    def sumofsquares(self):
        
        obsval = np.array([])
        modval_interp = np.array([])
        for imat in range(len(self.mat)):
            obsval = np.append(obsval, self.obs.data[imat].val)
            modval_interp = np.append(modval_interp, 
            self._interpolate(self.mod.data[imat].val,
            self.mod.data[imat].time, self.obs.data[imat].time))

        return np.sum((np.array(obsval) - np.array(modval_interp))**2.)

    def model(self, params):
        """ params ::   thr ths Alfa n Ks l
        in case of 2 soils paras list of two lists
        """
        cmd = './{} {}'.format(self.exe, self.hp)

        self.set_params(params)

        #os.system(cmd)

        tmp = self.read_modeled()
        self.mod = ModData(tmp[0], tmp[1], tmp[2])

        ss = self.sumofsquares()
        print (ss)
        #return (ss)

    def run(self):
        pass
        initparams = self.get_params()
        self.model(initparams)
