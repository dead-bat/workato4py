"""
    WORKATO ADMIN: Bulk-migrate contents of workspaces


"""

    # log is list of lists; fields are:
    # [ 
    #    [ <timestamp>, <status>, <error>, <message>, <operation>, <input>, <output> ],
    #    [ <timestamp>, <status>, <error>, <message>, <operation>, <input>, <output> ]
    # ]


import requests, json, sys, csv, time
from datetime import datetime


workato_config = {
    'us': ('https://www.workato.com', '<token>'),
    'eu': ('https://app.eu.workato.com', '<token>')
}

try:
    api_root, api_token = workato_config[sys.argv[1]]
    base_header = {"Authorization": f"Bearer {api_token}"}
    mlist = csv.reader(open(sys.argv[2], 'r'))
    wdict = json.load(open(sys.argv[3], 'r'))
except:
    print("Input error. Check your arguments and try again.")

## DEFINITIONS ##

def export_log(logfile, log):
    with open(f"bulk/{logfile}", 'w') as of:
        for line in log:
            text = "\"" + ("\", \"").join(log) + "\""
            of.write(text)

def download_package(source_ws, pkg_id):
    fn = f"bulk/{source_ws}_{pkg_id}.zip"
    package = { "data": fn, "log": [] }
    error_state = False
    try:
        target = f"{api_root}/api/managed_users/{source_ws}/exports/{pkg_id}"
        package['log'].append([datetime.now(), # timestamp
                            'get_package_meta', # status
                            False, # error
                            "Getting package metadata.", # message
                            "requests.get() used to query package status.", # operation
                            {
                                "api_root": api_root,
                                "package_status_endpoint": target,
                                "headers": base_header
                            }, # input
                            None]) # output
        # get package details from workato, to get download uri
        r = requests.get(target, headers=base_header)
        r_data, r_status = r.json()['result'], r.status_code
        while r_status in [200, 201] and r_data['status'] not in ['completed', 'failed', 'error']:
            time.sleep(3)
            r = requests.get(target, headers=base_header)
            r_data, r_status = r.json()['result'], r.status_code
            package['log'].append([ datetime.now(), 'get_package_meta', False, 'Waiting for package export to finish.', None, None, {"status": r_status, "text": r_data}])
        if r_data['status'] == 'completed':
            package['log'].append([datetime.now(), # timestamp
                                'get_package_meta', # status
                                False, # error
                                'Received reponse for package metadata request.', # message
                                None, # operation
                                None, # input
                                {
                                    "status": r_status,
                                    "text": r_data
                                }]) # output
        elif r_data['status'] in ['error', 'failed'] or r_status not in [200, 201]:
            package['log'].append([datetime.now(), 'get_package_meta', True, 'Failed to get package download URL. Request for package info failed.',
                                   "Get package metadata: API response error.", None, { "status": r_status, "text": r_data }])
            error_state = True
        if error_state == False:
            target = r_data['download_url']
            package['log'].append([datetime.now(), # timestamp
                                'download_start', # status
                                False, # error
                                "Beginning file download.", # message
                                "requests.get() streaming file download to temp file", # operation
                                { "download_url": target }, # input
                                None]) # output
            # download file from download uri; stream into fn for local copy; store binary data in package['data']
            r = requests.get(target, stream=True)
            with open(fn, 'wb') as of:
                for chunk in r.iter_content(chunk_size=128):
                    of.write(chunk)
            package['log'].append([datetime.now(), # timestamp
                                'download_finish', # status
                                False, # error
                                'Downloaded ZIP package.', # message
                                None, # operation
                                None, # input
                                f"File saved as {fn}"]) # output
    except Exception as ex:
        package['log'].append([datetime.now(),
                    None,
                    True,
                    "error",
                    ex,
                    None,
                    None])
        print(package['log'])
        #export_prompt = input("Export log for troubleshooting? [y/n]: ")
        #if export_prompt in ['y', 'Y']:
        #    edf = f"bulk_migrator_logdump-{datetime.now().strftime('%Y-%m-%d_%H-%M-%s')}.csv"
        #    export_log(edf, package['log'])
    else:
        return package

def import_package(dest_ws, dest_folder, pkg):
    import_header = {**base_header, 'content-type': 'application/octet-stream'}
    target = f"{api_root}/api/managed_users/{dest_ws}/imports?folder_id={dest_folder}"
    imported = { "meta": { "upload_to": target, "package_file": pkg['data'], "import_headers": import_header}, "log": [] }
    try:
        package = open(pkg['data'], 'rb')
        imported['log'].append([datetime.now(),
                                'import_start',
                                False,
                                "Package file opened. Queued to import.",
                                "open(pkg_file, 'rw')",
                                { 'pkg_file': pkg['data'] },
                                None])
        import_result = requests.post(target, headers=import_header, data=package)
        i_status, i_data = import_result.status_code, import_result.json()
        if 'id' not in i_data.keys():
            print(i_data)
            raise Exception(f"Abnormal reponse received while trying to import package {pkg['data']} to {target}.")
        pkg_id = i_data['id']
        while i_status in [200, 201] and i_data['status'] not in ['completed', 'failed', 'error']:
            time.sleep(3)
            target = f"{api_root}/api/managed_users/{dest_ws}/imports/{pkg_id}"
            import_result = requests.get(target, headers=base_header)
            i_status, i_data = import_result.status_code, import_result.json()
            imported['log'].append([datetime.now(),
                                    'import_in_progress',
                                    False,
                                    'Waiting for import to complete',
                                    'check import status',
                                    { 'workspace': dest_ws, 'import_id': pkg_id },
                                    { 'request_status': i_status, 'response': i_data }])
        if i_status in [200, 201] and i_data['status'] == 'completed':
            imported['log'].append([datetime.now(),
                                    'import_finish',
                                    False,
                                    'Waiting for import to complete',
                                    'check import status',
                                    { 'workspace': dest_ws, 'import_id': pkg_id },
                                    { 'request_status': i_status, 'response': i_data }])
        else:
            imported['log'].append([datetime.now(),
                                    'import_failed',
                                    True,
                                    'Import operation failed.',
                                    None,
                                    { 'workspace': dest_ws, 'import_id': pkg_id },
                                    { 'request_status': i_status, 'response': i_data }])
    except Exception as ex:
        package['log'].append([datetime.now(),
                    None,
                    True,
                    "error",
                    ex,
                    None,
                    None])
        print(package['log'])
        #export_prompt = input("Export log for troubleshooting? [y/n]: ")
        #if export_prompt in ['y', 'Y']:
        #    edf = f"bulk_migrator_logdump-{datetime.now().strftime('%Y-%m-%d_%H-%M-%s')}.csv"
        #    export_log(edf, package['log'])
    else:
        package.close()
        return imported


def process_migration(op_in):
    source_workspace = op_in['source_workspace']
    source_package = op_in['source_package_id']
    destination_workspace = op_in['destination_workspace']
    destination_folder = op_in['destination_folder']
    log = [[datetime.now(),
            "initializing", 
            False, 
            "Initializing migration.", 
            "Setting migration parameters.", 
            op_in, 
            {
                "source_workspace": source_workspace,
                "source_package": source_package,
                "destination_workspace": destination_workspace,
                "destination_folder": destination_folder
            }]]
    #log.append([datetime.now(),
    #            "initializing", 
    #            False, 
    #            "Initializing migration.", 
     #           "Setting migration parameters.", 
     #           op_in, 
     #           {
     #               "source_workspace": source_workspace,
     #               "source_package": source_package,
     #               "destination_workspace": destination_workspace,
     #               "destination_folder": destination_folder
     #           }])
    try:
        log.append([datetime.now(),
                    "download_package",
                    False,
                    "download_start",
                    "Calling download_package()",
                    {
                        "source_workspace": source_workspace,
                        "source_package": source_package
                    },
                    None])
        package = download_package(source_workspace, source_package)
        log.append([datetime.now(),
                    "download_package",
                    False,
                    "download_finish",
                    "Download package returned package successfully.",
                    None,
                    package['log']])
        log.append([datetime.now(),
                    "import_package",
                    False,
                    "import_start",
                    "Calling import_package()",
                    {
                        "destination_workspace": destination_workspace,
                        "destination_folder": destination_folder,
                        "source_package": package['data']
                    },
                    None])
        import_operation = import_package(destination_workspace, destination_folder, package)
        log.append([datetime.now(),
                    "import_package",
                    False,
                    "import_finish",
                    "Import finished successfully.",
                    None,
                    import_operation['log']])
    except Exception as ex:
        log.append([datetime.now(),
                    None,
                    True,
                    "error",
                    ex,
                    None,
                    None])
        print(log)
        #export_prompt = input("Export log for troubleshooting? [y/n]: ")
        #if export_prompt in ['y', 'Y']:
        #    edf = f"bulk_migrator_logdump-{datetime.now().strftime('%Y-%m-%d_%H-%M-%s')}.csv"
        #    export_log(edf, log)
    else:
        return log

def main(migrations, workspaces):
    print(f"{api_root}\n{api_token}\n{base_header}\n\n")
    operations = []
    log = []
    for m in migrations:
        migration = {
            'bsg_id': m[0],
            'source_package_id': m[1],
            'source_workspace': None,
            'destination_workspace': None,
            'destination_folder': None
        }
        for w in workspaces:
            if w['external_id'] == migration['bsg_id'] + "_DEV":
                migration['destination_workspace'] = w['id']
                for p in w['projects']:
                    if p['name'] in ['HOME', 'Home']:
                        migration['destination_folder'] = p['folder_id']
            elif w['external_id'] == migration['bsg_id']:
                migration['source_workspace'] = w['id']
        operations.append(migration)
    for op in operations:
        if None not in op.values():
            operation = process_migration(op)
            for m in operation:
                log.append(m)
        else:
            log.append([datetime.now(),
                        'operation_audit_failed',
                        True,
                        'check_operation_parameters_failed',
                        "One or more parameters are missing for operation.",
                        op,
                        None])
    export_log(f"operations_{datetime.now().strftime('%Y-%m-%d_%H-%M-%s')}.csv", log)
    print("Done.")

main(mlist, wdict)