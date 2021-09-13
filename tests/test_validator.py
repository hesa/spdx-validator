#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest

from spdx_validator.validator import SPDXValidator
from spdx_validator.validator import SPDXValidationException

class TestValidator(unittest.TestCase):
    
    def test_constructor(self):

        #
        # no arg constructor
        #
        validator = SPDXValidator()
        self.assertTrue(validator.spdx_version == "2.2")
        
        #
        # one arg constructor
        #
        validator = SPDXValidator("2.2")
        self.assertTrue(validator.spdx_version == "2.2")
        
        #
        # bad spdx version constructor
        #
        with self.assertRaises(SPDXValidationException):
            validator = SPDXValidator("2.1")


    def test_validate_file(self):

        validator = SPDXValidator()
        validator.validate_file("example-data/freetype.spdx.yml")

        with self.assertRaises(SPDXValidationException):
            validator.validate_file("example-data/freetype.spdx.notexistsing")

        with self.assertRaises(SPDXValidationException):
            validator.validate_file(None)


    def test_validate_data(self):
        import yaml

        validator = SPDXValidator()
        
        manifest_data = yaml.safe_load(open("example-data/freetype.spdx.yml"))
        validator.validate_json(manifest_data)

        with self.assertRaises(SPDXValidationException):
            validator.validate_json(None)

        with self.assertRaises(SPDXValidationException):
            validator.validate_json({})






            
        

