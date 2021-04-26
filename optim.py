import os

class Optim(object):
    
    def __init__(self,hydro_proj, outdir):
        self.hp = hydro_proj
        self.outdir = outdir
        self.exe = 'H1D_CALC.EXE'

    def model(self,params):
        cmd = './{} {}'.format(self.exe, self.hp)
        os.system(cmd)
        


    def run(self):
        pass
