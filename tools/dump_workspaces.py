"""
    dump_workspaces.py

    Dump details of every client workspace in Workato to a JSON file
"""

import requests, json

## Definitions

#### Global Vars

OUTPUT_FILE = 'data/workspace_details.json'
RHEAD = {'Authorization': 'Bearer <token>'}
API_ROOT = 'https://www.workato.com'

#### Functions

def get_managed_workspaces():
    """
    Returns a list of objects describing each managed user workspace
    """
    try:
        results = []
        target = f"{API_ROOT}/api/managed_users/"
        response = requests.get(target, headers=RHEAD)
        for result in response.json()['result']:
            results.append(result)
        target = f"{API_ROOT}/api/managed_users/"
        response = requests.get(target, headers=RHEAD, params={'page': '2'})
        for result in response.json()['result']:
            results.append(result)
        return results
        
    except:
        print(f"Failed to retrieve managed workspaces:\nStatus: {response.status_code}\nResponse: {response.text}\n")

def get_workspace_folders(workspace_id):
    """
    Returns a list of objects describing each folder in a managed user workspace
    """
    target = f"{API_ROOT}/api/managed_users/{workspace_id}/folders"
    try:
        
        response = requests.get(target, headers=RHEAD)
        return json.loads(response.text)['result']
    except:
        print(f"Failed to retrieve folders in workspace {workspace_id}:\nStatus: {response.status_code}\nResponse: {response.text}\n")

def get_workspace_projects(workspace_id):
    """
    Returns a list of objects describing each project in a managed user workspace
    """
    target = f"{API_ROOT}/api/managed_users/{workspace_id}/projects"
    try:
        response = requests.get(target, headers=RHEAD)
        return json.loads(response.text)['result']
    except:
        print(f"Failed to retrieve projects in workspace {workspace_id}:\nStatus: {response.status_code}\nResponse: {response.text}\n")

#def get_workspace_manifests(workspace_id):
#    """
#    Returns a list of objects describing each manifest in a managed user's workspace RLCM tool
#    """
#    manifests = []
#    return manifests

# 1
# Get all client workspaces; add to list
# clients = [ { "workato_id": 000000, "workspace_name": "Workspace Name", "external_id": "1111" },
#             { "workato_id": 000001, "workspace_name": "Workspace 2 Name", "external_id": "1112"}, ... ]

clients = get_managed_workspaces()
print(f"Found {len(clients)} managed workspaces...\n")
for client in clients:
    print(client['name'])
# 2A
# For each_workspace in clients, get all folders each_workspace; add to list
# clients = [ {'workato_id': 0000000, 'workspace_name': 'Workspace Name', 'external_id': '1111',
#              'folders': [ { 'folder_id': 9999999, 'folder_name': 'All Projects' },
#                            { 'folder_id': 8888888, 'folder_name': 'Dev'}, ... ] }, ... ]

for i in range( 0, len(clients) - 1 ):
    clients[i]['folders'] = get_workspace_folders(clients[i]['id'])


# 2B
# For each_workspace in clients, get all projects for each_workspace; add to list
# clients = [
#   {
#       'workato_id': 0000000, 'workspace_name': 'Workspace Name', 'external_id': '1111',
#       'folders': [ { 'folder_id': 9999999, 'folder_name': 'All Projects' }, ... ],
#       'projects': [ { 'project_id': 777777, 'project_name': 'Alpha Project', ... }, 
#                     { 'project_id': 777778, 'project_name': 'Beta Project', ... } ]
#   }
# ]

for i in range( 0, len(clients) - 1 ):
    clients[i]['projects'] = get_workspace_projects(clients[i]['id'])

# 2C (optional / if supported)
# For each_workspace in clients, get all RLCM manifests from each_workspace; add to list
# clients = [
#   {
#       'workato_id': 0000000, 'workspace_name': 'Workspace Name', 'external_id': '1111',
#       'folders': [ { 'folder_id': 9999999, 'folder_name': 'All Projects' }, ... ],
#       'projects': [ { 'project_id': 777777, 'project_name': 'Alpha Project' }, ... ],
#       'manifests': [
#           { 'manifest_id': 6666666, 'manifest_name': 'Manifest One', 'source_folder': 'All Projects', ... },
#           { 'manifest_id': 6666667, 'manifest_name': 'Manifest Two', 'source_folder': 'Dev', ... }
#       ]
#   },
#   ...
# ]

#for i in range( 0, len(clients) - 1 ):
#    clients[i]['manifests'] = get_workspace_manifests(clients[i]['id'])

# 3 - Export clients as JSON file

with open(OUTPUT_FILE, 'w') as of:
    of.write(json.dumps(clients, indent=4))

print("Done.")