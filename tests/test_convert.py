#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import sys
import unittest

from spdx_validator.convertor import SPDXConvertor
from spdx_validator.validator import SPDXValidator

class TestConvertor(unittest.TestCase):
    
    def test_yaml(self):
        validator = SPDXValidator()
        validator.validate_file("example-data/freetype.spdx.yml")

        convertor = SPDXConvertor(validator)
        
        json_data = convertor.convert("yaml")
        with self.assertRaises(json.decoder.JSONDecodeError):
            json.loads(json_data)
        
        json_data = convertor.convert("yaml")
        with self.assertRaises(json.decoder.JSONDecodeError):
            json.loads(json_data)
        
        json_data = convertor.convert("json")
        json.loads(json_data)
        
        

        
if __name__ == '__main__':
    unittest.main()
