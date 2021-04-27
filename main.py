#!/usr/bin/python

"""Optimize the parmaeters and the model Hydrus1D.
"""
__author__ = "Jakub Jerabek"
__license__ = "GPL"
__email__ = "jakub.jerabek@fsv.cvut.cz"

import os
import optim
from parser import read_parser

def main(pars):
    """ prepare the output directoiry 
    and init and run the optimization 
    """

    outdir = '{}.{}'.format(pars.hydrus_project.strip('/'), 'out')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    Optim = optim.Optim(pars.hydrus_project, outdir)
    Optim.run()

if __name__ == "__main__":
    main(read_parser())
