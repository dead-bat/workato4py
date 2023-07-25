"""
    WORKATO CI/CD PIPELINE
    Deploy Package from Dev Workspace to Client Workspace

    EXAMPLE

    python rlcm_pipeline.py <workato_env> <src_id> <src_workspace> <src_type> <dest_workspace> <dest_folder> <restart>

    ALL PARAMETERS ARE REQUIRED AND ARE AS FOLLOWS:
        <workato_env>       The Workato region to perform the deployment in ('us' or 'eu')
        <src_id>            The ID of the source manifest or package
        <src_workspace>     The ID of the source workspace (can be internal Workato ID or "E<external_id>" -- if external_id is 1234, it would be "E1234")
        <src_type>          The source type -- package or manifest -- of the src_id (manifests will be exported as packages before downloading)
        <dest_workspace>    The ID of the workspace to deploy to (can be internal Workato ID or "E<external_id>"; see above)
        <dest_folder>       The folder ID of the destination folder in the destination workspace
        <restart>           Set to 1 if you would like recipes to be restarted manually (when stopped during deployment); otherwise, 0

"""

import requests, json, sys, time, tempfile

## CONSTANTS

WORKATO_ENVS = {
    'us': ('https://www.workato.com', '<token>'),
    'eu': ('https://www.eu.workato.com', '<token>')
}
TEMP_DIR = tempfile.TemporaryDirectory()
PKG_DIR = TEMP_DIR.name

## FUNCTIONS
def generate_input(sys_args):
    in_obj = {
        "ops_params": {
            "workato_env": sys_args[1]
        },
        "src_params": {
            "id": sys_args[2],
            "src_workspace": sys_args[3],
            "pkg_type": sys_args[4]
        },
        "dest_params": {
            "dest_workspace": sys_args[5],
            "dest_folder": sys_args[6],
            "restart_recipes": sys_args[7]
        }
    }
    return in_obj

def global_config(src_data):
    api_root, api_token = WORKATO_ENVS[src_data['workato_env']]
    base_header = {'Authorization': f"Bearer {api_token}"}
    return api_root, base_header

def request_failed(message):
    print("API ERROR\n")
    print(message)
    print("\n")
    sys.exit("Aborting...")

def download_package(url, file_name):
    print("DOWNLOADING PACKAGE ZIP...")
    r = requests.get(url, stream=True)
    with open(f"{PKG_DIR}/{file_name}", 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    return file_name

def export_package(source_workspace, manifest_id):
    print("EXPORTING MANIFEST AS DOWNLOADABLE PACKAGE...")
    target = f"{API_ROOT}/api/managed_users/{source_workspace}/exports/{manifest_id}"
    export_operation = requests.post(target, headers=BASE_HEADER)
    response, r_code = json.loads(export_operation.text), export_operation.status_code
    ## test
    print(response, "\n", r_code)
    ##
    if r_code in [200, 201]:
        return response['id']
    else:
        request_failed(f"Error exporting package.\n\n{response}\n\n")

def get_package(package):
    print("GETTING PACKAGE FROM SOURCE WORKSPACE...")
    if package['pkg_type'] == 'manifest':
        package_id = export_package(package['src_workspace'], package['id'])
    else:
        package_id = package['id']
    target = f"{API_ROOT}/api/managed_users/{package['src_workspace']}/exports/{package_id}"
    response = requests.get(target, headers=BASE_HEADER)
    r_data, r_code = json.loads(response.text)['result'], response.status_code
    ## test
    print(r_data, "\n", r_code)
    ##
    while r_code in [200, 201] and r_data['status'] not in ['completed', 'failed', 'error']:
        time.sleep(3)
        response = requests.get(target, headers=BASE_HEADER)
        r_data, r_code = json.loads(response.text), response.status_code
        ## test
        print(r_data, "\n", r_code)
        ##
    if r_code in [200, 201] and r_data['status'] == 'completed':
        package = download_package(r_data['download_url'], f"{r_data['id']}.zip")
    else:
        request_failed("Package ID not available. Response:\n{r_data}")
    return package

def deploy_package(destination, package):
    print("DEPLOYING PACKAGE TO DESTINATION WORKSPACE...")
    up_headers = {**BASE_HEADER, 'Content-Type': 'application/octet-stream'}
    up_to = f"{API_ROOT}/api/managed_users/{destination['dest_workspace']}/imports?folder_id={destination['dest_folder']}"
    if destination['restart_recipes'] is True:
        up_to += '&restart_recipes=true' # UNTESTED
    pkg = open(f"{PKG_DIR}/{package}", 'rb')
    import_operation = requests.post(up_to, headers=up_headers, data=pkg)
    i_data, i_code = json.loads(import_operation.text), import_operation.status_code
    ## test
    print(i_data, "\n", i_code)
    ##
    while i_code in [200, 201] and i_data['status'] not in ['completed', 'failed', 'error']:
        time.sleep(3)
        target = f"{API_ROOT}/api/managed_users/{destination['dest_workspace']}/imports/{i_data['id']}"
        response = requests.get(target, headers=BASE_HEADER)
        i_data, i_code = json.loads(response.text), response.status_code
        ## test
        print(i_data, "\n", i_code)
        ##
    if i_code in [200, 201] and i_data['status'] == 'completed':
        return i_data
    else:
        request_failed(f"Package import failed. Response:\n{i_data}")

def deployment_report(result):
    dep_table_format = "{f:>20}:\t{v:<}"
    for field in result:
        if field != "recipe_status" and result[field] is not None:
            print(dep_table_format.format(f=field, v=result[field]))
    for rec in result['recipe_status']:
        print("\n")
        for field in rec:
            print(dep_table_format.format(f=field, v=rec[field]))
    print("\n\n")
    return True

## GLOBAL CONFIG

input_object = generate_input(sys.argv)
API_ROOT, BASE_HEADER = global_config(input_object['ops_params'])

## MAIN

def main(config):
    print(f"Using temporary directory: {PKG_DIR}.\n")
    solution_package = get_package(config['src_params'])
    imported_package = deploy_package(config['dest_params'], solution_package)
    print(f"Package deployed successfully!\n\nDETAILS:\n")
    deployment_report(imported_package)
    sys.exit("Exiting.")

main(input_object)

TEMP_DIR.cleanup()