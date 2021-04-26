#!/usr/bin/python
import os
import optim
from parser import read_parser

def main(pars):

    outdir = '{}.{}'.format(pars.hydrus_project.strip('/'), 'out')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    Optim = optim.Optim(pars.hydrus_project, outdir)
    Optim.run()

if __name__ == "__main__":
    main(read_parser())
