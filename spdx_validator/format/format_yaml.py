#!/usr/bin/python3

# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from spdx_validator.format.format_interface import FormatInterface

class YamlFormatter(FormatInterface):

    def __init__(self):
        pass
    
    def format_packages(self, packages):
        return yaml.safe_dump(packages)

    def convert(self, data):
        return yaml.safe_dump(data)

    
