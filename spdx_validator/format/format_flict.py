#!/usr/bin/python3

# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from spdx_validator.format.format_interface import FormatInterface

class FlictFormatter(FormatInterface):

    def __init__(self):
        pass

    def _package_to_flict(self, package):
        return {
            "name": package['SPDXID'],
            "license": package['licenseConcluded'],
            "dependencies": []
        }
        
    def _package_to_flict_project(self, package, deps):
        return {
            "project": {
                "name": package['SPDXID'],
                "license": package['licenseConcluded'],
                "dependencies": deps
            }
        }
        
    
    def format_packages(self, packages):
        package_list = []
        for p in packages:
            deps = []
            for dep in p['dependencies']:
                dep_map = self._package_to_flict(dep)
                deps.append(dep_map)
            top = self._package_to_flict_project(p['package'], deps)
            package_list.append(top)
        return json.dumps(package_list, indent=4)
    
                            
    
    def convert(self, data):
        return "no implementation for flict"
