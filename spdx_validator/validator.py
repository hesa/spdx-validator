#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import json
import jsonschema
import os
import sys
import yaml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEBUG = True

SPDX_VERSION_2_2 = "2.2"
SPDX_VERSIONS =[ SPDX_VERSION_2_2 ]


class SPDXValidationException(Exception):
    pass

class SPDXValidator:

    def __init__(self, spdx_version = SPDX_VERSION_2_2, schema_file = None, spdx_dirs = [], debug = False):
        self.debug = debug
        self.spdx_version = spdx_version
        self.checked_elements = []
        self.manifest_data = None
        if spdx_version not in SPDX_VERSIONS:
            raise SPDXValidationException("Unsupported SPDX version (" + str(spdx_version) + ")")

        if schema_file == None:
            schema_file = os.path.join(SCRIPT_DIR, "var/spdx-schema-" + spdx_version + ".json")
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)

        if spdx_dirs == []: 
            self.spdx_dirs = [ "." ]
        else:
            self.spdx_dirs = spdx_dirs

    def data(self):
        return self.manifest_data
            
    def validate_file(self, spdx_file, recursive = False):
        manifest_data = None
        self.verbose("Validate file: " + str(spdx_file))
        try:
            self.verbosen("Determine file suffix: ")
            filename, suff = os.path.splitext(spdx_file)
            self.verbose(" OK, " + str(suff))

            self.verbosen("Read data from file: ")
            with open(spdx_file, 'r') as f:
                if suff.lower() == ".yaml" or suff.lower() == ".yml":
                    manifest_data = yaml.safe_load(f) 
                elif suff.lower() == ".json":
                    manifest_data = json.load(f)
                else:
                    raise SPDXValidationException("Unsupported file type: " + str(spdx_file))
                self.verbose("OK")

         except Exception as e:
             if self.debug:
                 print(str(e), file=sys.stderr)
            raise SPDXValidationException("Could not open file: " + str(spdx_file))

        #
        # If no manifest data in object, this must be the top one
        # - store it
        #
        if self.manifest_data == None:
            self.manifest_data = manifest_data

        
        self.validate_json(manifest_data)
        if not recursive:
            return manifest_data

        if 'relationships' not in manifest_data:
            return manifest_data
        
        for relationship in manifest_data['relationships']:
            relation_type = relationship['relationshipType']
            if relation_type == 'DYNAMIC_LINK':
                elem_id = relationship['spdxElementId'].replace("DocumentRef-", "")
                related_elem = relationship['relatedSpdxElement']

                if elem_id in self.checked_elements:
                    self.verbose(elem_id + " is already check, continuing")
                    continue


                #
                # Validate that the (internal) element in the
                # relationship actually exists in the current SPDX
                # 
                self.verbosen("Validate internal element (" + related_elem + "): ")  
                self._validate_related_elem(related_elem, manifest_data)
                self.verbose("OK")

                #
                #
                #
                self.verbosen("Find file for element (" + elem_id + "): ")
                f = self._find_manifest_file(elem_id)
                self.verbose("OK")

                #
                # Validate this file 
                #
                inner_manifest = self.validate_file(f, recursive)

                #
                # Validate that inner manifest contains the reference (elem_id)
                #
                inner_name = inner_manifest['name']
                inner_name_found = False
                for inner_pkg in inner_manifest['packages']:
                    full_ref = inner_name + ":" + inner_pkg['SPDXID'] 
                    if full_ref == elem_id:
                        inner_name_found = True
                if not inner_name_found:
                    raise SPDXValidationException("Could not find: " + str(elem_id) + " in file: " + f)

                self.checked_elements.append(elem_id)
                

        return manifest_data

    def _find_manifest_file(self, elem_id):
        
        files = []
        # loop through all dirs to find matching files
        for dir in self.spdx_dirs:
            pkg_ver = elem_id.split(":")[0]
            pkg = pkg_ver.split("-")[0]
            ver = pkg_ver.split("-")[1]

            # create list of potential files
            try_files = []
            try_files.append(os.path.join(dir, pkg_ver) + ".json")
            try_files.append(os.path.join(dir, pkg_ver) + "-spdx.json")
            try_files.append(os.path.join(dir, pkg_ver) + ".spdx.json")
            try_files.append(os.path.join(os.path.join(dir, pkg), pkg_ver + ".json"))
            try_files.append(os.path.join(os.path.join(dir, pkg), pkg_ver + "-spdx.json"))
            try_files.append(os.path.join(os.path.join(dir, pkg), pkg_ver + ".spdx.json"))
            # try each potential file
            for f in try_files:
                # if present, store it
                if os.path.isfile(f):
                    files.append(f)

        #
        # Only, one (1) file should be found, otherwise raise exception
        #
        files_cnt = len(files)
        if files_cnt == 0:
            raise SPDXValidationException("Could not find manifest file for : " + str(elem_id))
            
        if files_cnt > 1:
            raise SPDXValidationException("Found " + str(files_cnt) + " manifest files for : " + str(elem_id))

        return files[0]

    def _validate_related_elem(self, item, manifest_data):
        found = False
        for pkg in manifest_data['packages']:
            spdx_id = pkg['SPDXID']
            if spdx_id == item:
                found = True
        if not found:
            raise SPDXValidationException("Could not find related element: " + str(item))
        
    
    def validate_json(self,  manifest_data):
        try:
            self.verbosen("Validating spdx data : ")
            jsonschema.validate(instance=manifest_data,
                                schema=self.schema)
            self.verbose("OK")

        except jsonschema.exceptions.ValidationError as exc:
            raise SPDXValidationException(exc)

        return True
        
    def err(self, msg, file=sys.stderr, end="\n"):
        print(msg, file=file, end=end)
    
    def verbose(self, msg, file=sys.stderr, end="\n"):
        if self.debug:
            self.err(msg, file, end)

    def verbosen(self, msg, file=sys.stderr, end=""):
        if self.debug:
            self.err(msg, file, end)

    
        
