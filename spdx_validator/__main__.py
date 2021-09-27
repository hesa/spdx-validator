#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


from argparse import RawTextHelpFormatter
import argparse
import sys

from spdx_validator.format.factory import FormatFactory
from spdx_validator.format.factory import supported_formats

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

    parser.add_argument('-dc', '--discard-checksum',
                        action='store_true',
                        dest='discard_checksum',
                        help="Do not control checksum of spdx documents.",
                        default=False)

    parser.add_argument('file',
                        help='file to validate',
                        nargs='?',
                        default=None)
    
    parser.add_argument('--spdx-version',
                        help='SPDX version to validate against. Supported versions: ' + str(SPDX_VERSIONS),
                        type=str,
                        default=SPDX_VERSION_2_2)
    
    parser.add_argument('--convert', 
                        help='Convert a package in one format to another. ',
                        action='store_true',
                        default=False)
    
    parser.add_argument('--format', '-f',
                        help='Output format. Supported formats: ' + str(supported_formats()),
                        type=str,
                        default="JSON")
    
    parser.add_argument('--schema-file', '-sf',
                        help='Schema file (JSON) to use, instead of the built in',
                        type=str,
                        default=None)
    
    parser.add_argument('--recursive', '-r',
                        help='Check validity recursively (all relations)',
                        action='store_true',
                        default=False)
    
    parser.add_argument('--spdx-dir', '-sd',
                        dest='spdx_dirs',
                        help='Directories where to look for spdx files.',
                        type=str,
                        nargs="+",
                        default=[])
    
    parser.add_argument('--print-packages', '-pp',
                        help='After validaiton print packages (and dependencies).',
                        action='store_true',
                        default=False)
        
    args = parser.parse_args()

    return args

def main():

    args = parse()    
    file_name = args.file
    
    
    #
    # Create validator object
    # 
    validator = SPDXValidator(args.spdx_version,
                              args.schema_file,
                              args.spdx_dirs,
                              args.verbose)


    #
    # Aaaaand your money's gone.
    # ... kidding, let's validate
    # 
    formatter = FormatFactory.formatter(args.format)
    try:
        data = validator.validate_file(file_name, args.recursive, discard_checksum = args.discard_checksum)
        if args.print_packages:
            deps = validator.packages_deps()
            formatted = formatter.format_packages(deps)
            print(formatted)
    except Exception as e:
        print("Failed validating: " + file_name, file=sys.stderr)
        print(e, file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)
    if args.convert:
        if args.format is None:
            print("Can't convert file " + file_name + ". Missing format.", file=sys.stderr)
            exit(10)
        else:
            print(formatter.convert(validator.data()))
            exit(0)
    else:
        exit(0)

if __name__ == '__main__':
    main()

