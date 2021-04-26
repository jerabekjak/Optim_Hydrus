import os
import numpy as np

class Data(object):
    def __init__(self, time, val, position):
        self._n = len(time)
        self.time = np.zeros(self._n, float)
        self.val = np.zeros(self._n, float)
        self.positoin = np.zeros(self._n, float)

        self.time = [float(i) for i in time]
        self.val = [float(i) for i in val]
        self.position = [int(i) for i in position]

class Optim(object):
    
    def __init__(self,hydro_proj, outdir):
        self.hp = hydro_proj
        self.outdir = outdir
        self.exe = 'H1D_CALC.EXE'

        tmp = self.read_measured()
        self.obs = Data(tmp[0], tmp[1], tmp[2])

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

    def model(self, params):
        """ params ::   thr ths Alfa n Ks l
        in case of 2 soils paras list of two lists
        """
        cmd = './{} {}'.format(self.exe, self.hp)

        self.set_params(params)

        #os.system(cmd)

        ss = sumofsquares()
        return (ss)

    def run(self):
        pass
        #initparams = self.get_params()
        #self.model(initparams)
