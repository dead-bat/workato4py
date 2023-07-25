"""
    WORKATO: BULK CREATE WORKSPACES
    Create new managed customer workspaces in Workato from CSV list

    EXAMPLE

    $ python create_workspace.py <source_file>

    All arguments are required. The parameters are as follows:

        source_file     The source CSV from which to read the workspaces to be created
        
"""

import requests, json, sys, time, tempfile, csv
import workato_oem

## CONSTANTS AND GLOBAL CONFIG

TOKENS = {
    'us': '<token>',
    'eu': '<token>'
}

## FUNCTIONS

def generate_workspaces_list(src_file):
    workspaces = []
    src_list = csv.reader(open(src_file, 'r'), delimiter=',')
    for wksp in src_list:
        workspaces.append({'name': wksp[1], 'backstop_id': wksp[0], 'region': wksp[2]})
    return workspaces

## MAIN

def main(input):
    workspaces = generate_workspaces_list(input)
    for workspace in workspaces:
        print(f"Creating workspaces for {workspace['name']} in region \"{workspace['region']}\".\n\tBSG_ID: {workspace['backstop_id']}\n")
        # create Workato connection object
        wk_api = workato_oem.Workato(workspace['region'], TOKENS[workspace['region']])
        # create Dev workspace
        print("Creating Dev workspace...")
        try:
            dev_ws = wk_api.create_workspace(f"{workspace['name']} Dev", f"{workspace['backstop_id']}_DEV", 'integrations-testing@backstopsolutions.com')
        except Exception as ex:
            print(f"Exception occurred:\n{ex}")
        else:
            if dev_ws.status_code in [200, 201]:
                print(dev_ws.data)
                print(f"Successfully created Dev workspace for {workspace['name']}.\n")
            else:
                print(f"FAILED! Something went wrong:\n{dev_ws.message}\n")
        # create Prod workspace
        print("Creating prod workspace...")
        try:
            prod_ws = wk_api.create_workspace(workspace['name'], workspace['backstop_id'], 'integrations@backstopsolutions.com')
        except Exception as ex:
            print(f"Exception occurred:\n{ex}")
        else:
            if prod_ws.status_code in [200, 201]:
                print(prod_ws.data)
                print(f"Successfully created Prod workspace for {workspace['name']}.\n")
            else:
                print(f"FAILED! Something went wrong:\n{prod_ws.message}")
        time.sleep(3)
    sys.exit("Complete. Exiting...")

main(sys.argv[1])