"""This modelu the Hydrus1D model directory in the program.
"""
import argparse
import textwrap

def read_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
         Optimize HYDRUS1D (Simunek) with scipy optmization methos
         ---------------------------------------------------------
         The directory needs to contain the Fit.out file. The optimization
         needs to be run at least once with the Hydru1d.exe. Measured
         data are extracted from the Fit.out file. 
         '''))

    parser.add_argument(
        '-hp',
        '--hydrus_project',
        help='directory of the HYDRUS1D project',
        type=str,
        required=True
    )

    return parser.parse_args()
