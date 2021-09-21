#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import jsonschema
import os
import sys
import yaml

CONVERTOR_FORMAT_JSON = "json"
CONVERTOR_FORMAT_YAML = "yaml"
CONVERTOR_FORMATS = [ CONVERTOR_FORMAT_JSON, CONVERTOR_FORMAT_YAML ]

class SPDXConvertor:

    def __init__(self, validator):
        self.validator = validator

    def convert(self, out_format):
        if out_format.lower() == CONVERTOR_FORMAT_JSON:
            return self.convert_json()
        elif out_format.lower() == CONVERTOR_FORMAT_YAML:
            return self.convert_yaml()

    def convert_json(self):
        return json.dumps(self.validator.data())

    def convert_yaml(self):
        return yaml.safe_dump(self.validator.data())


