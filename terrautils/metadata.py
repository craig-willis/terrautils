"""Metadata
This module provides useful reference methods for accessing and cleaning TERRA-REF metadata.
"""

import json
import os
import pyclowder.datasets

import lemnatec
from terrautils.sensors import Sensors


def clean_metadata(json, sensorId):
    """ Given a metadata object, returns a cleaned object with standardized structure 
        and names.
    """
    if 'lemnatec_measurement_metadata' in json.keys():
        cleaned = lemnatec.clean(json, sensorId)
    else:
        return None

    cleaned["terraref_cleaned_metadata"] = True
    return cleaned


def get_terraref_metadata(clowder_md, sensor_id=None, station='ua-mac'):
    """Crawl Clowder metadata object and return TERRARef metadata or None.

    If sensor_id given, will attach fixed sensor metadata from that sensor."""

    terra_md = {}

    if 'terraref_cleaned_metadata' in clowder_md:
        terra_md = clowder_md
    else:
        for sub_metadata in clowder_md:
            if 'content' in sub_metadata:
                sub_metadata = sub_metadata['content']
            if 'terraref_cleaned_metadata' in sub_metadata and sub_metadata['terraref_cleaned_metadata']:
                terra_md = sub_metadata

    # Add sensor fixed metadata
    if sensor_id:
        sensor_fixed = get_sensor_fixed_metadata(station, sensor_id)
        if 'sensor_fixed_metadata' in terra_md:
            sensor_fixed['url'] = terra_md['sensor_fixed_metadata']['url']
        terra_md['sensor_fixed_metadata'] = sensor_fixed

    return terra_md


def get_extractor_metadata(clowder_md, extractor_name):
    """Crawl Clowder metadata object for particular extractor metadata and return if found."""
    for sub_metadata in clowder_md:
        if 'agent' in sub_metadata:
            sub_md = sub_metadata['agent']
            if 'name' in sub_md and sub_md['name'].find(extractor_name) > -1:
                return sub_md

    return None


def get_preferred_synonym(variable):
    """Execute a thesaurus check to see if input variable has alternate preferred name."""
    pass


def get_sensor_fixed_metadata(station, sensor_id, host='', key=''):
    """Get fixed sensor metadata from Clowder."""
    if not host:
        host = os.getenv("CLOWDER_HOST", 'https://terraref.ncsa.illinois.edu/clowder/')
    if not key:
        key = os.getenv("CLOWDER_KEY", '')

    s = Sensors(base="", station=station, sensor=sensor_id)
    datasetid = s.get_fixed_datasetid_for_sensor(station, sensor_id)
    jsonld = pyclowder.datasets.download_metadata(None, host, key, datasetid)

    for sub_metadata in jsonld:
        if 'content' in sub_metadata:
            # TODO: Currently assumes only one metadata object attached to formal sensor metadata dataset
            return sub_metadata['content']


if __name__ == "__main__":
    # TODO: Either formalize these tests a bit or remove
    fixed = get_sensor_fixed_metadata("ua-mac", "VNIR")
    print "\nFIXED METADATA"
    print json.dumps(fixed[0]["content"], indent=4, sort_keys=True)

    print "\nCLEANED METADATA"
    with open("/data/terraref/sites/ua-mac/raw_data/VNIR/2017-05-13/2017-05-13__12-29-21-202/cd2a45b6-4922-48b4-bc29-f2f95e6206ec_metadata.json") as file:
        json_data = json.load(file)
    cleaned = clean_metadata(json_data, "VNIR")
    print json.dumps(cleaned, indent=4, sort_keys=True)
