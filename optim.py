import os

class Optim(object):
    
    def __init__(self,hydro_proj, outdir):
        self.hp = hydro_proj
        self.outdir = outdir
        self.exe = 'H1D_CALC.EXE'

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

    def set_params(self):
        pass

    def model(self, params):
        """ params ::   thr ths Alfa n Ks l
        in case of 2 soils paras list of two lists
        """
        cmd = './{} {}'.format(self.exe, self.hp)
        os.system(cmd)

    def run(self):
        initparams = self.get_params()
