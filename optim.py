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
        file_ = '{}/{}'.format(self.hp, 'SELECTOR.IN')
        with open(file_,'r') as f:
            lines = f.readlines()
        NMat = int(lines[13].split()[0])



    def model(self, params):
        """ params ::   thr ths Alfa n Ks l
        in case of 2 soils paras list of two lists
        """
        cmd = './{} {}'.format(self.exe, self.hp)

        self.set_params(params)



        #os.system(cmd)

    def run(self):
        initparams = self.get_params()
        self.model(initparams)
