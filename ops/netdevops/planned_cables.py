from pprint import pprint
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

netbox_url = "https://192.168.111.8"
auth_token = "584149a859ea8e7a7f5e2d610c7235a3e2d2460c"
headers = {
    'Authorization': f"Token {auth_token}",
    'Content-Type': f'application/json',
    'Accept': f'application/json'
}

url = f"{netbox_url}/graphql/"

def query_planned_cables():
    query_planned_cables = '''
        query planned_cables {
            cable_list(filters: { status: "connected" }) {
                id
                display
                label
                description
                comments
                status
                a_terminations {
                    ... on InterfaceType {
                        id
                        name
                        device {
                            name
                        }
                    }
                }
                b_terminations {
                    ... on InterfaceType {
                        id
                        name
                        device {
                            name
                        }
                    }
                }
            }
        }'''
    return query_planned_cables

# get data for planned cables from netbox
response_planned_cables = requests.post(url, json={"query": query_planned_cables()}, headers=headers, verify=False)

for planned_cable in response_planned_cables.json()['data']['cable_list']:

    a_terminations = planned_cable['a_terminations']
    b_terminations = planned_cable['b_terminations']

    if len(a_terminations) != 1:
        pprint(f"Unexpected number of terminations for a_termination: {len(a_terminations)}")
        continue

    if len(b_terminations) != 1:
        pprint(f"Unexpected number of terminations for b_termination: {len(b_terminations)}")
        continue

    a_termination = a_terminations[0]
    b_termination = b_terminations[0]

    # get the device of each termination-endpoint
    print(f"Cable-ID: #{planned_cable['id']}, A-Ende: {a_termination['device']['name']}: {a_termination['name']}, B-Ende: {b_termination['device']['name']}: {b_termination['name']}")
