import argparse
import textwrap

def read_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
         Optimize HYDRUS1D (Simunek) with scipy optmization methos
         ---------------------------------------------------------
         '''))

    parser.add_argument(
        '-hp',
        '--hydrus_project',
        help='directory of the HYDRUS1D project',
        type=str,
        required=True
    )

    return parser.parse_args()
