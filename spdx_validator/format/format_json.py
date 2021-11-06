#!/usr/bin/python3

# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from spdx_validator.format.format_interface import FormatInterface

class JsonFormatter(FormatInterface):

    def __init__(self):
        pass
    
    def format_packages(self, package, packages, package_name = None):
        return json.dumps(packages)

    def convert(self, data):
        return json.dumps(data)
    
