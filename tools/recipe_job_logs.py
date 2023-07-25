"""
    Get Recipe and Job Details from Workato API

    USAGE
        $ python recipe_job_logs.py -w <workspace> -r <recipe_id> [-j <job_id> | -a]

        workspace   the name of the workspace, as defined in the workatoApiWorkspaces
                    dictionary within the script.

        recipe_id   the recipe ID (can be retrieved from the URL in Workato's web UI)

        -j <job_id> to collect details of a specific job, provide the -j switch and the
                    job ID (from the URL in Workato's web UI)

                    OR
                
                -a  use the -a switch to get summary details of all jobs for recipe_id
"""

import requests, sys, os, json
from oldconfig import workatoApiBaseUrl, workatoApiWorkspaces, dataDirectory

workspace, recId, jobId, allJobs = None, None, None, False

for i in range(1, len(sys.argv)):
    if sys.argv[i] == '-w':
        workspace = sys.argv[i+1]
    if sys.argv[i] == '-r':
        recId = sys.argv[i+1]
    if sys.argv[i] == '-j':
        jobId = sys.argv[i+1]
    if sys.argv[i] == '-a':
        allJobs = True

if workspace == None:
    workspace = input("Enter workspace name: ")
if recId == None:
    recId == input("Enter recipe ID: ")
if allJobs == False and jobId == None:
    getAll = input("Get all jobs? [y/n] ").upper()
    if getAll == 'Y':
        allJobs = True
    else:
        jobId == input("Enter job ID: ")
outFileName = input("Enter output file name (blank for default): ")


env = workatoApiWorkspaces[workspace]['env']
authType = workatoApiWorkspaces[workspace]['authType']
baseUrl = workatoApiBaseUrl[env]

# Request format:
# curl -X GET <base_api_url>+<endpoint_subdir> -H 'x-user-token:<api_key>', -H 'x-user-email:<user_email>'

if authType == 0:
    em, ak = workatoApiWorkspaces[workspace]['cred']
    headers = {'x-user-token': ak, 'x-user-email': em}
elif authType == 1:
    token = workatoApiWorkspaces[workspace]['cred']
    headers = {'Authorization': "Bearer %s" % token}

print("CONFIG PROFILE:\n\tRecipe ID: %s\n\tWorkspace: %s\n\tEnvironment: %s\n\t%s" % (recId, workspace, env, baseUrl))

if allJobs is True:
    target = baseUrl + 'recipes/' + recId + '/jobs'
    if outFileName == '':
        outFileName = workspace + "_" + recId + "_alljobs"
    logDir = dataDirectory + "/recipes/"
else:
    target = baseUrl + 'recipes/' + recId + '/jobs/' + jobId
    if outFileName == '':
        outFileName = workspace + "_" + recId + "-" + jobId
    logDir = dataDirectory + "/jobs/"

try:
    os.mkdir(logDir)
except OSError:
    pass

response = requests.get(target, headers=headers)
data = json.loads(response.text)
pretty = json.dumps(data, indent=4)

with open(logDir + outFileName + ".json", "w") as of:
    of.write(pretty)

print("Done!")