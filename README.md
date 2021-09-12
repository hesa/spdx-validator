# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

# spdx-validator

Simple validator of package SBoM

# Installation

```
git https://github.com/hesa/spdx-validator.git
cd spdx-validator
pip install .
```

# Supported SPDX versions

* [2.2](https://github.com/spdx/spdx-spec/blob/development/v2.2.1/schemas/spdx-schema.json)

## Supported formats

* yaml

* JSON

# Using spdx_validator

## Basic use

Assuming you have a SPDX file, `project.json`, you would like to validate:

```
$ spdx-validator project.json
$ echo $?
0
```

If you don't see any printout and the return code is `0`, the file is valid.

## Verbose printut

Assuming you have a SPDX file, `project.spdx.yaml`, you would like to validate:

```
$ spdx-validator example-data/project.spdx.yml --verbose
Determine file suffix:  OK, .yml
Read data from file: OK
Validating spdx data : OK
$ echo $?
0
```
