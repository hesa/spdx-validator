#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import jsonschema
import os
import sys
import yaml

class SPDXConvertor:

    def __init__(self, validator):
        self.validator = validator
        pass

    def convert(self, out_format):
        if out_format.lower() == "json":
            return self.convert_json()
        elif out_format.lower() == "yaml" or format.lower() == "yml":
            return self.convert_yaml()
            
    def convert_json(self):
        return json.dumps(self.validator.data())

    def convert_yaml(self):
        return   yaml.safe_dump(self.validator.data())

