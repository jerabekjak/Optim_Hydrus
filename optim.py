"""This modelu prepares and performs the optimization of the model Hydrus1D

This modelu read the observer data from existing Fit.out file. It read the
modeled data after the Hydrus computation finishes and compare the modeled and
measured data. The scipy.potimize package is then used to performs the
optimization of parameters. 
"""

__author__ = "Jakub Jerabek"
__license__ = "GPL"
__email__ = "jakub.jerabek@fsv.cvut.cz"

import os
import numpy as np
import math
import shutil
from sys import platform
from scipy.interpolate import interp1d
from scipy.optimize import differential_evolution
from scipy.optimize import minimize

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
    def __init__(self, time, val, position, nmat):

        time = np.array([float(i) for i in time])
        val = np.array([float(i) for i in val])
        position = np.array([int(i) for i in position])
        self.nmat = nmat

        self.data = []
        for ipos in np.unique(position):
            which = ipos == position
            self.data.append(Data(time[which], val[which], position[which]))
        
class ModData(object):
    def __init__(self, time, val, position, nmat):

        time = np.array([float(i) for i in time])
        val = np.array([float(i) for i in val])
        position = np.array([int(i) for i in position])
        self.nmat = nmat

        self.data = []
        for ipos in np.unique(position):
            which = ipos == position
            self.data.append(Data(time[which], val[which], position[which]))
        


class Optim(object):
    
    def __init__(self, hydro_proj, outdir):
        self.hp = hydro_proj
        self.outdir = outdir

        if platform == "linux" or platform == "linux2":
            self.exe = 'wine H1D_CALC.EXE'
            self.cmd = '{} {}'.format(self.exe, self.hp)
        elif platform == "win32":
            self.exe = 'H1D_CALC.EXE'
            self.cmd = './{} {}'.format(self.exe, self.hp)
        else: 
            import sys
            sys.exit('unknown platform')

        tmp = self.read_measured()
        self.obs = ObsData(tmp[0], tmp[1], tmp[2], tmp[3])
        self.nmat = self.obs.nmat
        self.obsnodes = len(self.obs.data)

        self.err = '{}{}'.format(self.hp, 'Error.msg')
        if os.path.exists(self.err):
            os.remove(self.err)

        if os.path.exists(self.outdir):
            shutil.rmtree(self.outdir)
        os.mkdir(self.outdir)

        self.outfile = open('{}/{}'.format(self.outdir, 'rrsqrt-pamameters.txt'),'w')
        self.Counter = 0

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
        
        nparams = len(params)
        nmat = self.nmat

        i = 0
        for i in range(nmat): # replace lines in selector
            ii = range(i*(nparams/nmat),((i+1)*nparams/nmat))
            p = params[ii]
            str_ = ' '.join([str(elem) for elem in p]) + '\n'
            lines[26+i] = str_

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
            line = lines[i].replace('*', ' ').split()
            for imat in range(self.obsnodes):
                cval = imat*3+1
                try: 
                    float(line[ctime])
                    time.append(line[ctime])
                    val.append(line[cval])
                    position.append(imat)
                except:
                    print ('error lines')

        return time, val, position, self.nmat

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

        file_ = '{}/{}'.format(self.hp, 'SELECTOR.IN')
        with open(file_,'r') as f:
            lines = f.readlines()
        NMat = int(lines[13].split()[0])

        return time, val, position, NMat

    def _interpolate(self, val, time, time2):
        f = interp1d(time, val)
        return f(time2)

    def sumofsquares(self):
        
        obsval = np.array([])
        modval_interp = np.array([])
        for imat in range(self.obsnodes):
            obsval = np.append(obsval, self.obs.data[imat].val)
            modval_interp = np.append(modval_interp, 
            self._interpolate(self.mod.data[imat].val,
            self.mod.data[imat].time, self.obs.data[imat].time))

        return np.sum((np.array(obsval) - np.array(modval_interp))**2.)

    def model(self, params):
        """ params ::   thr ths Alfa n Ks l
        in case of 2 soils paras list of two lists
        """
        newresults = '{}.{}'.format(os.path.split(self.outdir)[1],
            str(self.Counter).zfill(4))
        self.Counter += 1

        params[2] = 10**params[2]
        params[8] = 10**params[8]

        self.set_params(params)

        # RUN HYDRUS
        os.system(self.cmd)

        if os.path.exists(self.err):
            os.remove(self.err)
            ss = 100000
            str_ = ' '.join([str(elem) for elem in params])
            outline = '{} {}\n'.format(ss, str_)
            self.outfile.write(outline)
            return (ss)


        shutil.copytree(self.hp, '{}/{}'.format(self.outdir, newresults))

        tmp = self.read_modeled()
        self.mod = ModData(tmp[0], tmp[1], tmp[2], tmp[3])

        ss = self.sumofsquares()
        str_ = ' '.join([str(elem) for elem in params])
        outline = '{} {}\n'.format(ss, str_)
        self.outfile.write(outline)
        print (ss)

        return (ss)

    def run(self):
        pass
        bounds = [(0,0.2),(0.25,0.3),(-4, -1), (1.25, 1.37), (2, 10), (0.5,0.5),
                  (0,0.05),(0.25,0.3),(-4, -1), (1.21, 1.37), (2, 10), (0.5,0.5)]
        #bounds = [0.2,0.5,0.014, 1.25, 10, 0.5,
        #          0.2,0.5,0.014, 1.25, 10, 0.5]
        differential_evolution(self.model, bounds)
        #minimize(self.model, bounds, method='CG')
