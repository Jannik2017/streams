from pprint import pprint
import json
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

netbox_url = "https://192.168.111.205"
auth_token = "584149a859ea8e7a7f5e2d610c7235a3e2d2460c"
headers = {
    'Authorization': f"Token {auth_token}",
    'Content-Type': f'application/json',
    'Accept': f'application/json'
}

url = f"{netbox_url}/graphql/"

def query_device_interfaces_function(device):
    query_device_interfaces = '''
    query {
        device_list(filters: {name: {exact: "''' + device + '''"}}) {
            name
            interfaces {
                name
                ip_addresses {
                    address
                    tags {
                        name
                    }
                }
                tags {
                    name
                }  
            }
            custom_fields
        }
    }
    '''
    return query_device_interfaces
    #return device

query_devices_p1 = '''
query {
    device_list(filters: {name: {starts_with: "p1r"}}) {
        name
    }
}
'''

# get data from netbox
response_devices_p1 = requests.post(url, json={"query": query_devices_p1}, headers=headers, verify=False)

for device in response_devices_p1.json()['data']['device_list']:
    response_device_interfaces = requests.post(url, json={"query": query_device_interfaces_function(device['name'])}, headers=headers, verify=False)
    pprint(response_device_interfaces.json())

