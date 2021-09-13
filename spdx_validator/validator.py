#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import jsonschema
import os
import sys
import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

DEBUG = True

SPDX_VERSION_2_2 = "2.2"
SPDX_VERSIONS =[ SPDX_VERSION_2_2 ]

class SPDXValidationException(Exception):
    pass

class SPDXValidator:

    def __init__(self, spdx_version = SPDX_VERSION_2_2, debug = False):
        self.debug = debug
        self.spdx_version = spdx_version
        if spdx_version not in SPDX_VERSIONS:
            raise SPDXValidationException("Unsupported SPDX version (" + str(spdx_version) + ")")
            
        with open(os.path.join(SCRIPT_DIR, "var/spdx-schema-" + spdx_version + ".json"), 'r') as f:
            self.schema = json.load(f)

    def validate_file(self, spdx_file):

        try:
            self.verbosen("Determine file suffix: ")
            filename, suff = os.path.splitext(spdx_file)
            self.verbose(" OK, " + str(suff))

            self.verbosen("Read data from file: ")
            with open(spdx_file, 'r') as f:
                if suff.lower() == ".yaml" or suff.lower() == ".yml":
                    manifest_data = yaml.safe_load(f) 
                elif suff.lower() == ".json":
                    manifest_data = json.load(f)
                else:
                    raise SPDXValidationException("Unsupported file type: " + str(spdx_file))
        except:
            raise SPDXValidationException("Could not open file: " + str(spdx_file))
        self.verbose("OK")
        
        return self.validate_json(manifest_data)
        
    def validate_json(self, json_data):
        try:
            self.verbosen("Validating spdx data : ")
            jsonschema.validate(instance=json_data,
                                schema=self.schema)
            self.verbose("OK")

        except jsonschema.exceptions.ValidationError as exc:
            raise SPDXValidationException(exc)

    def err(self, msg, file=sys.stderr, end="\n"):
        print(msg, file=file, end=end)
    
    def verbose(self, msg, file=sys.stderr, end="\n"):
        if self.debug:
            self.err(msg, file, end)

    def verbosen(self, msg, file=sys.stderr, end="\n"):
        if self.debug:
            self.err(msg, file, end)

    
        
