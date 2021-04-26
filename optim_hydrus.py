#!/usr/bin/python
import os
from parser import read_parser

def main(pars):
    print (pars)

    outdir = '{}.{}'.format(pars.hydrus_project.strip('/'), 'out')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

if __name__ == "__main__":
    main(read_parser())
