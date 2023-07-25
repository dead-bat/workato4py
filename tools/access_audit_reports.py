"""
    WORKATO: USERS, ROLES, WORKSPACES REPORTS
    General reports for auditing Workato access and authorization.

    EXAMPLE:

    $ python access_audit_reports.py <workato_env>

    Where <workato_env> is the regional Workato environment (ie., 'us' or 'eu'). The output will be three HTML files, as follows:

        - workato_roles_<date>.html
          Provides a summary of user roles defined in the root Workato workspace (the "Backstop Integrator team space") that are
          made available across all child workspaces (ie., they are 'inheritable') which are used to manage what users can and cannot
          do in workspaces they are members of.
        - user_membership_by_workspace_<date>.html
          Details which users are members of which workspace, and what they're associated role is in each workspace. This can be used
          to determine which users have access to which workspaces, and what permissions they have in the workspace. It also provides
          details about the status of their account and most recent activity.
        - users_with_deployment_permissions_<date>.html
          A short report that highlights the users who have the "Deployment Engineer" role in any one or more workspaces. Users with
          this role have a unique ability to make changes (within limits) to production workspaces and, therefore, need to be monitored
          explicitly for security purposes.
    
    This suite of reports can be used, primarily, for quarterly audits of Workato users and permissions. When these are due, a ticket
    (like https://jira.backstop.solutions/browse/SYSTEMS-11774) will be generated and the reports provided by this pipeline will suffice
    to fulfill the requirements of the ticket.

    Output files are stored in ./data, relative to the filesystem location of this script.

"""

import requests, json, datetime, sys

## CONSTANTS

WORKATO_ENVS = {
    'us': ('https://www.workato.com', '<token>'),
    'eu': ('https://app.eu.workato.com', '<token>')
}
API_ROOT, API_TOKEN = WORKATO_ENVS[sys.argv[1]]
BASE_HEADER = {'Authorization': f"Bearer {API_TOKEN}"}
RUNTIME = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
REPORT_DIR = './data/reports' # 'data/reports'

## FUNCTIONS

def generate_roles_report():
    report_title = "Workato User Roles"
    results = {
        'report': f"<html><head><title>{report_title}</title></head><body><header><h1>{report_title}</h1></header><main>",
        'error': False
    }
    target = f"{API_ROOT}/api/roles"
    response = requests.get(target, headers=BASE_HEADER)
    if response.status_code in [200, 201]:
        results['report'] += "<table><tr><th>Role ID</th><th>Role Name</th><th>Role Permissions</th></tr>"
        roles = json.loads(response.text)
        for role in roles:
            results['report'] += f"<tr><td>{role['id']}</td><td>{role['name']}</td><td>{role['privileges']}</td></tr>"
        results['report'] += f"</table></main><hr /><footer>{RUNTIME}</footer></body></html>"
    else:
        results['report'] = response.text
        results['error'] = True
    return results

def generate_workspace_members_report():
    report_title = "Workato Users by Workspace"
    results = {
        'report': f"<html><head><title>{report_title}</title></head><body><header><h1>{report_title}</h1></header><main>",
        'error': False,
        'dep_eng': []
    }
    target = f"{API_ROOT}/api/managed_users"
    response = requests.get(target, headers=BASE_HEADER)
    if response.status_code in [200, 201]:
        workspaces = json.loads(response.text)['result']
        results['report'] += "<table><tr><th>User Name</th><th>User ID</th><th>Role In Workspace</th></tr>"
        for wksp in workspaces:
            results['report'] += f"<tr><td colspan=\"3\"><strong>{wksp['name']}</strong> ({wksp['external_id']})</td></tr>"
            target = f"{API_ROOT}/api/managed_users/{wksp['id']}/members"
            response2 = requests.get(target, headers=BASE_HEADER)
            if response2.status_code in [200, 201]:
                wksp_members = json.loads(response2.text)
                for mem in wksp_members:
                    results['report'] += f"<tr><td>{mem['name']}</td><td>{mem['id']}</td><td>{mem['role_name']}</td></tr>"
                    if mem['role_name'] == 'Deployment Engineer':
                        results['dep_eng'].append({'member_id': mem['id'], 'member_name': mem['name'], 'workspace': wksp['name'], 'workspace_ext_id': wksp['external_id']})
            else:
                results['report'] += f"<tr><td colspan=\"3\"><em>ERROR OCCURRED RETRIEVING WORKSPACE MEMBERS</em></td></tr>"
        results['report'] += f"</table></main><footer>{RUNTIME}</footer></body></html>"
    else:
        results['report'] = response.text
        results['error'] = True
    return results

def generate_deployers_report(deployers):
    report_title = "Workato Users with Deployment Permissions"
    results = {
        'report': f"<html><head><title>{report_title}</title></head><body><header><h1>{report_title}</h1></header><main><table>",
        'error': False
    }
    dep_eng = {}
    for each in deployers:
        if str(each['member_id']) not in dep_eng.keys():
            dep_eng[str(each['member_id'])] = { 'name': each['member_name'], 'workspaces': [{'name': each['workspace'], 'external_id': each['workspace_ext_id']}]}
        else:
            dep_eng[str(each['member_id'])]['workspaces'].append({'name': each['workspace'], 'external_id': each['workspace_ext_id']})
    for de in dep_eng:
        results['report'] += f"<tr><th><strong>{dep_eng[de]['name']}</strong> <em>(Workato ID: {de})</em></th></tr>"
        for ws in dep_eng[de]['workspaces']:
            results['report'] += f"<tr><td>{ws['name']}</td><td>External ID: {ws['external_id']}</td></tr>"
    #
    results['report'] += f"</table></main><footer>{RUNTIME}</footer></body></html>"
    return results

def export_report(data, filename):
    out_file = f"{REPORT_DIR}/{filename}" #f"{filename}" #f"{REPORT_DIR}/{filename}"
    if data['error'] is False:
        with open(out_file, 'w') as of:
            of.write(data['report'])
    else:
        print("Encountered an error. No report available. Details:\n")
        print(data['report'])
    return None

## MAIN

def main():
    roles = generate_roles_report()
    export_report(roles, f"workato_roles_{sys.argv[1]}_{RUNTIME}.html")
    wksp_members = generate_workspace_members_report()
    export_report(wksp_members, f"user_membership_by_workspace_{sys.argv[1]}_{RUNTIME}.html")
    dep_eng = generate_deployers_report(wksp_members['dep_eng'])
    export_report(dep_eng, f"users_with_deploy_permissions_{sys.argv[1]}_{RUNTIME}.html")
    return None

main()