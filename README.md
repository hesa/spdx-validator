<!--
SPDX-FileCopyrightText: 2020 Henrik Sandklef <hesa@sandklef.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

&nbsp;

[![REUSE status][1]][2]

[1]: https://api.reuse.software/badge/github.com/hesa/spdx-validator
[2]: https://api.reuse.software/info/github.com/hesa/spdx-validator

# spdx-validator

Simple validator of package SBoM

# Installation

```
git https://github.com/hesa/spdx-validator.git
cd spdx-validator
pip install .
```

# Supported SPDX versions

* [2.2](https://spdx.github.io/spdx-spec/) through this [JSON schema](https://github.com/spdx/spdx-spec/blob/development/v2.2.1/schemas/spdx-schema.json)

## Supported formats

* yaml

* JSON

# Using spdx_validator

## Basic use

Assuming you have an SPDX file, `project.json`, you would like to validate:

```
$ spdx-validator project.json
$ echo $?
0
```

If you don't see any printout and the return code is `0`, the file is valid.

## Verbose printut

Assuming you have an SPDX file, `project.spdx.yaml`, you would like to validate:

```
$ spdx-validator example-data/project.spdx.yml --verbose
Determine file suffix:  OK, .yml
Read data from file: OK
Validating spdx data : OK
$ echo $?
0
```

## Recursive use

As above you have an SPDX file, `project.json`, you would like to
validate. But this time you want to check all the relationships
recursively.

```
$ spdx-validator project.json -r
$ echo $?
0
```

If you don't see any printout and the return code is `0`, the file is valid.

# License

The program is licensed under GPL-3.0-only

The data (in the var directory) may be under other licenses.
