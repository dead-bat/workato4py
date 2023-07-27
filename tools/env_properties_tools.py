"""
    WORKATO: Environment Properties Tool

    python env_properties_tool.py <region> <src_workspace> <dest_workspace> <properties_prefix>

    workspaces are id'd by external_id (not workato id) -- do not include 'E' prefix.
    properties_prefix is optional (and doesn't do anything yet, anyway) but will allow to filter by
      property prefix in the future.
    
"""

import json, sys
import workato

workato_tokens = {
    'us': ('https://www.workato.com', '<token>')
    'eu': ('https://www.eu.workato.com', '<token>')
}

region = sys.argv[1]
src = sys.argv[2]
dest = sys.argv[3]

wkto = workato.Workato(region, workato_tokens[region])

def get_properties_from_workspace(workspace, workato_connection = workato.Workato, prefix=''):
    results = {}
    target = f"/api/managed_users/E{workspace}/properties?prefix={prefix}"
    r = workato_connection.api_request('get', target)
    if r.status_code not in [200, 201]:
        raise Exception(f"get_properties_from_workspace(): Invalid response from Workato.\n{r.status_code}\n{r.message}")
    else:
        if r.data['result']:
            results['properties'] = r.data['result']
        else:
            raise Exception(f"get_properties_from_workspace(): No properties returned for {workspace}.\n{r.data}")
    return results

def upsert_properties_to_workspace(workspace, workato_connection = workato.Workato, properties=None):
    result = []
    if type(properties) is not dict():
        raise Exception("upsert_properties_to_workspace(): No dictionary of properties provided.")
    target = f"/api/managed_users/E{workspace}/properties"
    r = workato_connection.api_request('post', target, payload=json.dumps(properties))
    if r.status_code not in [200, 201]:
        raise Exception(f"upsert_properties_to_workspace(): Upsert operation received abnormal response.\n{r.status_code}\n{r.message}")
    else:
        if r.data['success'] is True:
            result = [True]
        else:
            result = [False, r.data]
    return result

def copy_properties(workato_connection, source_workspace, destination_workspace):
    # get properties from source
    props_to_copy = get_properties_from_workspace(source_workspace, workato_connection)
    # push to destination
    copied = upsert_properties_to_workspace(destination_workspace, workato_connection, props_to_copy)
    return None

copy_properties(wkto, src, dest)
