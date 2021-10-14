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
            "name": package['name'],
            "license": package['licenseConcluded'],
            "dependencies": []
        }
        
    def _package_to_flict_project(self, package, deps):
        return {
            "project": {
                "name": package['name'],
                "license": package['licenseConcluded'],
                "dependencies": deps
            }
        }
        
    
    def format_packages(self, package, packages, package_name = None):
        package_list = []
        for _p in packages:
            p = _p['package']
            dependencies = _p['dependencies']
            if package_name != None and package_name != p['name']:
                continue
            deps = []
            for d in dependencies:
                deps.append(self._package_to_flict(d))
            top = self._package_to_flict_project(p, deps)
            package_list.append(top)

        if package_name != None:
            if len(package_list) == 1:
                return json.dumps(package_list[0], indent=4)
            else:
                return json.dumps(package_list, indent=4)
        else:
            return json.dumps(package_list, indent=4)
    
    def _format_package(self, package, dependencies):
        print("package: " + str(package['name']))
        print("dependencies: " + str(dependencies))
        for dep in dependencies:
            print(" ----- : " + str(dep))
    
    def convert(self, data):
        return "no implementation for flict" 
