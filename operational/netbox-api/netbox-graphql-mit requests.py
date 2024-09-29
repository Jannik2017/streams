from pprint import pprint
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

def generate_config_lines(neighbor, device, asn):
    config_lines = f"""
    set protocols bgp neighbor { neighbor } address-family ipv4-unicast nexthop-self
    set protocols bgp neighbor { neighbor } description '{ device }'
    set protocols bgp neighbor { neighbor } remote-as '{ asn }'
    set protocols bgp neighbor { neighbor } update-source 'lo'
    """
    return config_lines

def query_device_interfaces(device):
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

query_devices_p1 = '''
query {
    device_list(filters: {name: {starts_with: "p1r"}}) {
        name
    }
}
'''

# get data from netbox
response_devices_p1 = requests.post(url, json={"query": query_devices_p1}, headers=headers, verify=False)

# print result
bgp_config = {}
for device in response_devices_p1.json()['data']['device_list']:
    device_interfaces = requests.post(url, json={"query": query_device_interfaces(device['name'])}, headers=headers, verify=False)
    
    print("Device: " + device['name'])
    bgp_config[device['name']] = {}
    for interface in device_interfaces.json()['data']['device_list'][0]['interfaces']:
        if len(interface['ip_addresses']) > 0:
            for ip in interface['ip_addresses']:
                for tag in ip['tags']:
                    if tag['name'].startswith('route-reflector'):
                        print("Interface: " + ip['address'] + " is " + tag['name'])
                        bgp_config[device['name']]['rr-type'] = tag['name']
                        bgp_config[device['name']]['ipv4-address'] = ip['address']
                        bgp_config[device['name']]['asn'] = device_interfaces.json()['data']['device_list'][0]['custom_fields']['BGP_ASN']

route_reflectors = []
route_reflector_clients = []

# This loop iterates through the routers and their configurations.
for router, config in bgp_config.items():
    if 'rr-type' in config and config['rr-type'] == 'route-reflector':
        route_reflectors.append([router, config['ipv4-address']])
    else:
        route_reflector_clients.append([router, config['ipv4-address']])
    
# This loop iterates through the route reflectors and their clients, printing each client for each route reflector.
for route_reflector in route_reflectors:
    print(f"Route Reflector {route_reflector[0]} has the following clients:")
    for client in route_reflector_clients:
        config_lines = generate_config_lines(client[1], client[0], bgp_config[client[0]]['asn'])
        print(config_lines)

for client in route_reflector_clients:
    print(f"Client {client[0]} has the following route-reflectors:")
    for route_reflector in route_reflectors:
        config_lines = generate_config_lines(route_reflector[1], route_reflector[0], bgp_config[route_reflector[0]]['asn'])
        print(config_lines)

