#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import hashlib

from spdx_validator.exception import SPDXValidationException

HASH_SHA1 = "SHA1"
HASH_SHA224 = "SHA224"
HASH_SHA256 = "SHA256"
HASH_SHA384 = "SHA384"
HASH_SHA512 = "SHA512"
HASH_MD2 = "MD2"
HASH_MD4 = "MD4"
HASH_MD5 = "MD5"
HASH_MD6 = "MD6"

def hash_from_file(file_name, hash_name):
    hash_fun = None
    if hash_name.upper() == HASH_SHA1:
        hash_fun = hashlib.sha1
    elif hash_name.upper() == HASH_SHA224:
        hash_fun = hashlib.sha224
    elif hash_name.upper() == HASH_SHA256:
        hash_fun = hashlib.sha256
    elif hash_name.upper() == HASH_SHA384:
        hash_fun = hashlib.sha384
    elif hash_name.upper() == HASH_SHA512:
        hash_fun = hashlib.sha512
    elif hash_name.upper() == HASH_MD5:
        hash_fun = hashlib.md5
    else: # HASH_MD2,  HASH_MD6
        raise SPDXValidationException("Unsupported checksum format (" + str(hash_name) + ")")

    with open(file_name, 'rb') as f:
        f_bytes = f.read()
        #print("hash.... " + str(f_bytes))
        cs = hash_fun(f_bytes).hexdigest()
        #print("hash.... " + str(cs))
        return cs
    
