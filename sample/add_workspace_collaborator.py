"""
    WORKATO: ADD WORKSPACE COLLABORATORS
    Add collaborators to a managed customer workspace in Workato

    EXAMPLE

    $ python add_workspace_collaborator.py <env> <workspace_id> "<collaborator_name>:<collaborator_email>:<collaborator_role>"

    All arguments are required. Note that the collaborator name, e-mail, and role are a single string, encapsulated in quotes, with the values
    separated by semicolons. You may add as many collaborators in this format as you would like.

        <env>                   The Workato regional environment to create the worksapce(s) in ('us' or 'eu')
        <workspace_id>          The Workato external ID of the workspace (usually "<backstop_id>" for prod and "<backstop_id>_DEV" for dev)
        <collaborator_name>     The first and last name of the collaborator (eg. "John Smith")
        <collaborator_email>    The collaborator's e-mail address for their Workato account (typically their company e-mail)
        <collaborator_roel>     The name of the Workato role to assign to the collaborator in the workspace. This will typically be one of:
                                    - Integration Engineer Dev
                                    - Integration Engineer Prod
                                    - Integration Manager
                                    - QA Analyst
                                    - Deployment Engineer

    So, to add three users -- John Doe, Jane Smith, and Mickey Mouse -- to the Dev workspace for client 9999 in US, you would use:

    $ python add_workspace_collaborotor.py us 9999_DEV "John Doe:john.doe@backstopsolutions.com:Integrator Engineer Dev" \
      "Jane Smith:jsmith@backstopsolutions.com:Integration Manager" "Mickey Mouse:mmouse@disney.com:Special Privileges"
"""

import requests, json, sys, time

## CONSTANTS AND GLOBAL CONFIG

WORKATO_ENVS = {
    'us': ('https://www.workato.com', '<token>'),
    'eu': ('https://www.eu.workato.com', '<token>')
}

API_ROOT, API_TOKEN = WORKATO_ENVS[sys.argv[1]]
BASE_HEADER = {'Authorization': f"Bearer {API_TOKEN}", 'Content-Type': 'application/json'}

## FUNCTIONS

def generate_collaborators(input_array):
    input_object = []
    for i in input_array:
        j = i.split(":")
        entity = {
            'name': j[0],
            'email': j[1],
            'role_name': j[2]
        }
        input_object.append(entity)
    return input_object

def add_collaborator(user, workspace):
    results = {
        'input': user,
        'response': None,
        'error': False,
        'error_message': None
    }
    target = f"{API_ROOT}/api/managed_users/E{workspace}/member_invitations"
    response = requests.post(target, headers=BASE_HEADER, data=json.dumps(user))
    if response.status_code in [200, 201]:
        results['response'] = json.loads(response.text)
    else:
        results['error'] = True
        results['error_message'] = json.loads(response.text)
    return results

## MAIN

def main(workspace, raw_collaborators):
    new_members = generate_collaborators(raw_collaborators)
    for each in new_members:
        results = add_collaborator(each, workspace)
        if results['error'] == True:
            print(f"Failed to add collaborator to {workspace}. Error:\n{results['error_message']}")
        else:
            print(f"Successfully added collaborator. Response:\n{results['response']}")
        time.sleep(3)
    sys.exit("Complete. Exiting...")

main(sys.argv[2], sys.argv[3:])