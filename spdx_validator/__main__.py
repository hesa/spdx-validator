#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


from argparse import RawTextHelpFormatter
import argparse
import sys

from spdx_validator.validator import SPDXValidator
from spdx_validator.validator import SPDX_VERSION_2_2
from spdx_validator.validator import SPDX_VERSIONS

PROGRAM_NAME = "spdx-validator"
PROGRAM_DESCRIPTION = "spdx-validator is a Free and Open Source Software tool to validate SPDX"
PROGRAM_URL = "https://github.com/hesa/spdx-validator"
BUG_URL = "https://github.com/hesa/spdx-validator/issues"
PROGRAM_COPYRIGHT = "(c) 2021 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE = "GPL-3.0-or-later"
PROGRAM_AUTHOR = "Henrik Sandklef"
PROGRAM_ATTRIBUTION = "spdx-validator uses\n"
PROGRAM_ATTRIBUTION += "  * SPDX 2.2 schema from:\n"
PROGRAM_ATTRIBUTION += "    https://github.com/spdx/spdx-spec/blob/development/v2.2.1/schemas/spdx-schema.json\n" 

PROGRAM_SEE_ALSO = ""

def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"

    epilog = ""
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "PROJECT SITE\n  " + PROGRAM_URL + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  Create an issue at " + BUG_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + \
        PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "ATTRIBUTION\n  " + PROGRAM_ATTRIBUTION + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter,
    )
    
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information to stderr',
                        default=False)

    parser.add_argument('file',
                        help='file to validate',
                        nargs='?',
                        default=None)
    
    parser.add_argument('--spdx-version',
                        help='SPDX version to validate against. Supported versions: ' + str(SPDX_VERSIONS),
                        type=str,
                        default=SPDX_VERSION_2_2)
    
    args = parser.parse_args()

    return args

def main():

    args = parse()    
    file_name = args.file
    
    
    #
    # Create validator object
    # 
    validator = SPDXValidator(args.spdx_version, args.verbose)
    
    #
    # Aaaaand your money's gone.
    # ... kidding, let's validate
    # 
    try:
        validator.validate_file(file_name)
        exit(0)
    except Exception as e:
        print("Failed validating: " + file_name, file=sys.stderr)
        print(e, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    main(sys.argv)

