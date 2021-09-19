#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import subprocess
import unittest

from spdx_validator.validator import SPDXValidator
from spdx_validator.validator import SPDXValidationException

from spdx_validator.checksum import HASH_SHA1 
from spdx_validator.checksum import HASH_SHA224 
from spdx_validator.checksum import HASH_SHA256 
from spdx_validator.checksum import HASH_SHA384 
from spdx_validator.checksum import HASH_SHA512 
from spdx_validator.checksum import HASH_MD2 
from spdx_validator.checksum import HASH_MD4 
from spdx_validator.checksum import HASH_MD5 
from spdx_validator.checksum import HASH_MD6 
from spdx_validator.checksum import hash_from_file


def os_checksum(file, hash_name):
    hash_cmd = None
    if hash_name.upper() == HASH_SHA1:
        hash_cmd = "sha1sum " + file
    elif hash_name.upper() == HASH_SHA224:
        hash_cmd = "sha224sum " + file
    elif hash_name.upper() == HASH_SHA256:
        hash_cmd = "sha256sum " + file
    elif hash_name.upper() == HASH_SHA384:
        hash_cmd = "sha384sum " + file
    elif hash_name.upper() == HASH_SHA512:
        hash_cmd = "sha512sum " + file
    elif hash_name.upper() == HASH_MD5:
        hash_cmd = "md5sum " + file
    else: # HASH_MD2,  HASH_MD6
        raise SPDXValidationException("Unsupported checksum format (" + str(hash_name) + ")")
    
    res_raw = subprocess.check_output(hash_cmd, shell=True)
    res = str(res_raw.decode("utf-8"))
    cs = res.split(" ")[0]
    return cs

def validate_checksums(file, algo):
    print("algo: " + algo, file=sys.stderr)
    internal_cs = hash_from_file(file, algo)
    os_cs = os_checksum(file, algo)
    return internal_cs == os_cs
    
class TestChecksum(unittest.TestCase):

    def test_checksums(self):
        self.assertTrue(validate_checksums("setup.py", HASH_SHA1))
        self.assertTrue(validate_checksums("setup.py", HASH_SHA224))
        self.assertTrue(validate_checksums("setup.py", HASH_SHA256))
        self.assertTrue(validate_checksums("setup.py", HASH_SHA384))
        self.assertTrue(validate_checksums("setup.py", HASH_SHA512))
        self.assertTrue(validate_checksums("setup.py", HASH_MD5))

if __name__ == '__main__':
    unittest.main()
