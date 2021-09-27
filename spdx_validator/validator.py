#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import json
import jsonschema
import logging
import os
import sys
import yaml

from spdx_validator.checksum import hash_from_file
from spdx_validator.exception import SPDXValidationException

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEBUG = True

SPDX_VERSION_2_2 = "2.2"
SPDX_VERSIONS =[ SPDX_VERSION_2_2 ]

class SPDXValidator:

    def __init__(self, spdx_version = SPDX_VERSION_2_2, schema_file = None, spdx_dirs = [], debug = False):
        self.debug = debug
        self.spdx_version = spdx_version
        self.checked_packages = {}
        self.manifest_data = None
        self.all_manifests = {}
        self.dependencies = {}
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

        debug_level = logging.INFO
        if self.debug:
            debug_level = logging.DEBUG
            
        logging.basicConfig(format='%(asctime)s:   %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=debug_level)
        
    def data(self):
        return self.manifest_data

    def _dep_list(self, spdx_id, indent = ""):
        dependencies = []
        if spdx_id in self.dependencies:
            #print(indent + "     " + spdx_id + "   deps: " + str(self.dependencies[spdx_id]))
            for dep in self.dependencies[spdx_id]:
                if dep not in dependencies:
                    dependencies.append(dep)
                dependencies += self._dep_list(dep.split(":")[1], indent + "   ")
                #print(indent + "        d: " + str(dep))
        return dependencies
                
        
    def packages_deps(self):
        packages = []
        top_name = self.manifest_data['name']
        for pkg in self.manifest_data['packages']:
            pkg_spdx_id = pkg['SPDXID']
            pkg_key = top_name + ":" + pkg_spdx_id
            checked_pkg = self.checked_packages[pkg_key]
            dependencies = self._dep_list(pkg_spdx_id)
            package = {}
            package['package'] = checked_pkg
            package['dependencies'] = []
            #package['name'] = pkg_key
            #package['license'] = checked_pkg['licenseConcluded']
            #package['dependencies'] = []
            for dep in dependencies:
                package['dependencies'].append(self.checked_packages[dep])
            #    dep_map = {}
            #    dep_map[self.checked_packages[dep]['SPDXID']] = self.checked_packages[dep]
                #dep_map['name'] = self.checked_packages[dep]['SPDXID']
                #dep_map['license'] = self.checked_packages[dep]['licenseConcluded']
                #dep_map['dependencies'] = []
            #    package['dependencies'].append(dep_map)
            packages.append(package)
        #print(json.dumps(packages))
            #if pkg['SPDXID'] in self.dependencies:
            #    print("   d: " + str(self.dependencies[pkg['SPDXID']]))
        return packages
    
    def validate_file(self, spdx_file, recursive = False, discard_checksum = False):

        manifest_data = None
        logging.debug("Validate file: " + str(spdx_file))
        try:
            logging.debug("Determine file suffix ")
            filename, suff = os.path.splitext(spdx_file)
            logging.debug(" file suffix: " + str(suff))

            logging.debug("Read data from file ")
            with open(spdx_file, 'r') as f:
                if suff.lower() == ".yaml" or suff.lower() == ".yml":
                    manifest_data = yaml.safe_load(f) 
                elif suff.lower() == ".json":
                    manifest_data = json.load(f)
                else:
                    raise SPDXValidationException("Unsupported file type: " + str(spdx_file))
                logging.debug(" data read")

        except Exception as e:
            if self.debug:
                print(str(e), file=sys.stderr)
                raise SPDXValidationException("Could not open file: " + str(spdx_file))
        if manifest_data == None:
            raise SPDXValidationException("Could not open file: " + str(spdx_file))
    
        self.all_manifests[manifest_data['documentNamespace']] = manifest_data

        #
        # If no manifest data in object, this must be the top one
        # - store it
        #
        if self.manifest_data == None:
            self.manifest_data = manifest_data
            for pkg in manifest_data['packages']:
                elem_id = manifest_data['name'] + ":" + pkg['SPDXID'] 
                self.checked_packages[elem_id] = pkg

        self.validate_json(manifest_data)
        if not recursive:
            return manifest_data

        if 'relationships' not in manifest_data:
            return manifest_data
        
        #
        # Loop through the relationships in this manifest
        # - if linked ("DYNAMIC_LINK")
        #   validate it
        #
        for relationship in manifest_data['relationships']:
            logging.debug("Validating relationships")
            relation_type = relationship['relationshipType']
            if relation_type == 'DYNAMIC_LINK':
                elem_id_doc_ref = relationship['spdxElementId'].split(":")[0]
                elem_id = relationship['spdxElementId'].replace("DocumentRef-", "")
                related_elem = relationship['relatedSpdxElement']

                #print(" relationship: " + related_elem + "  ---uses---> "  + elem_id)
                if related_elem not in self.dependencies:
                    self.dependencies[related_elem] = []
                self.dependencies[related_elem].append(elem_id)
                    
                if elem_id in self.checked_packages:
                    logging.debug(" * " + elem_id + " is already check, continuing")
                    #print(" ignore: " + str(elem_id))
                    continue

                spdx_doc = None
                for doc_ref in manifest_data["externalDocumentRefs"]:
                    if elem_id_doc_ref == doc_ref['externalDocumentId']:
                        spdx_doc = doc_ref['spdxDocument']

                #
                # Validate that the (internal) element in the
                # relationship actually exists in the current SPDX
                # 
                logging.debug(" * " + "Validate internal element (" + related_elem + ") ")  
                self._validate_related_elem(related_elem, manifest_data)
                logging.debug(" *   element validated")

                #
                #
                #
                logging.debug(" * " + "Find file for element (" + str(spdx_doc) + ")")
                f = None
                if spdx_doc != None:
                    f = self._find_manifest_file(spdx_doc)
                logging.debug(" *   file for element found: " + str(f))


                #
                # Validate checksum
                #
                logging.debug(" * " + "Check checksum")
                ext_doc_ref = elem_id.split(":")[0]
                ext_doc_ref_found = False
                # - find checksum in external doc refs
                #print("manifest_data:" + str(manifest_data))
                if "externalDocumentRefs" not in manifest_data:
                    print("WHAT???? f:    " + str(f))
                    print("WHAT???? spdx: " + str(f))
                    print(str(manifest_data))
                    exit(1)

                #print(" * rel: " + elem_id + "   " + " coming from: " + related_elem)


                #
                # for every doc in "externalDocumentRefs" 
                # - check if we can find the current relationship's. If so, all fine
                #   otherwise, raise exception
                #
                if "externalDocumentRefs" not in manifest_data or manifest_data["externalDocumentRefs"] == []:
                    ext_doc_ref_found = True
                else:
                    for doc_ref in manifest_data["externalDocumentRefs"]:
                        external_doc_id = doc_ref['externalDocumentId']
                        # if not external, continue
                        if external_doc_id.startswith("DocumentRef-"):
                            ext_doc_ref_found = True
                            continue
                        else:
                            doc_ref_id = external_doc_id.split(":")[0].replace("DocumentRef-", "")
                            print("doc_ref_id: " + doc_ref_id)
                            # if id in ref list is the same as the file (f)
                            if ext_doc_ref == doc_ref_id:
                                print("yes ..." + str(ext_doc_ref))
                                # then control the checksums are the same
                                check_sum_algorithm = doc_ref['checksum']['algorithm']
                                check_sum = doc_ref['checksum']['checksumValue']
                                f_check_sum = hash_from_file(f, check_sum_algorithm)
                                if not discard_checksum:
                                    if f_check_sum != check_sum:
                                        raise SPDXValidationException("Checksum for " + str(f) + " (" + str(f_check_sum+ ") is not the same as in the \"externalDocumentRefs\" in " + str(spdx_file)))
                                ext_doc_ref_found = True
                if not ext_doc_ref_found:
                    raise SPDXValidationException("Could not find " + str(ext_doc_ref) + " in \"externalDocumentRefs\" in " + str(spdx_file))
                logging.debug(" *   checksum correct")

                        
                #
                # Validate this file 
                #
                if f != None:
                    logging.debug(" * ---> " + " Validate file " + f)
                    inner_manifest = self.validate_file(f, recursive, discard_checksum)
                    logging.debug(" * <--- " + " Validate file: " + f)


                    #
                    # Validate that inner manifest contains the reference (elem_id)
                    #
                    inner_name = inner_manifest['name']
                    inner_name_found = False
                    inner_pkg = None
                    for _inner_pkg in inner_manifest['packages']:
                        full_ref = inner_name + ":" + _inner_pkg['SPDXID'] 
                        if full_ref == elem_id:
                            inner_name_found = True
                            inner_pkg = _inner_pkg
                    if not inner_name_found:
                        raise SPDXValidationException("Could not find: " + str(elem_id) + " in file: " + f)
                
                    self.checked_packages[elem_id] = inner_pkg
                

        return manifest_data

    def OBSOLETE_suggest_file(self, elem_id):
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

        return files
    
    def _find_manifest_file(self, file_name):
        files = []
        # loop through all dirs to find matching files
        for dir in self.spdx_dirs:
            # create list of potential files
            try_files = []
            try_files.append(os.path.join(dir, file_name))
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
            raise SPDXValidationException("Could not find manifest file for : " + str(file_name))
            
        if files_cnt > 1:
            raise SPDXValidationException("Found " + str(files_cnt) + " manifest files for : " + str(file_name))

        logging.debug("files[0]: " + str(files[0]))
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
            logging.debug("Validating spdx data")
            jsonschema.validate(instance=manifest_data,
                                schema=self.schema)
            logging.debug("  spdx data validated")

        except jsonschema.exceptions.ValidationError as exc:
            raise SPDXValidationException(exc)

        return True
        
