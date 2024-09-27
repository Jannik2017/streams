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

url = 'https://192.168.111.205/graphql/' 
query_device_interfaces = '''
query {
    device_list(filters: {name: {exact: "p1r7v"}}) {
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

query_config_templates = '''
query {
    config_template(id: 1) {
        template_code
    }
}
'''

# get data from netbox
response_device_interfaces = requests.post(url, json={"query": query_device_interfaces}, headers=headers, verify=False)
response_config_templates = requests.post(url, json={"query": query_config_templates}, headers=headers, verify=False)

# print ip address information from query_device_interfaces
pprint(response_device_interfaces.json())

# # print config template
# lines_config_templates = response_config_templates.json()['data']['config_template']['template_code'].split('\r\n')
# for line in lines_config_templates:
#     print(line)
