#!/usr/bin/python3

# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


from spdx_validator.format.format_json import JsonFormatter
from spdx_validator.format.format_yaml import YamlFormatter
from spdx_validator.format.format_flict import FlictFormatter

FORMAT_JSON = "json"
FORMAT_YAML = "yaml"
FORMAT_FLICT = "flict"
FORMATS = [ FORMAT_JSON, FORMAT_YAML ]


class FormatFactory:

    _instance = None

    @staticmethod
    def formatter(format):
        if FormatFactory._instance is None:
            if format.lower() == "json":
                FormatFactory._instance = JsonFormatter()
            elif format.lower() == "yaml" or format.lower() == "yml":
                FormatFactory._instance = YamlFormatter()
            elif format.lower() == "flict":
                FormatFactory._instance = FlictFormatter()

        return FormatFactory._instance

def supported_formats():
    return FORMATS

