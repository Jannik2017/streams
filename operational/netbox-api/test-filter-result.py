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

rr_ips = []
rrc_ips = []

response_devices_p1 = requests.post(url, json={"query": query_devices_p1}, headers=headers, verify=False)

# print result
for device in response_devices_p1.json()['data']['device_list']:

    # Query the specific device's interfaces using its name
    device_interfaces = requests.post(url, json={"query": query_device_interfaces(device['name'])}, headers=headers, verify=False)

    # Extract the interfaces for this device from the response
    interfaces =  device_interfaces.json()['data']['device_list'][0]['interfaces']
    custom_fields = device_interfaces.json()['data']['device_list'][0]['custom_fields']

    # Iterate over each interface and its associated IP addresses with route-reflector tags
    for interface in interfaces:
        for address in interface['ip_addresses']:
            for tag in address['tags']:

                # Check if this is a route-reflector or route-reflector-client IP address
                if tag['name']=='route-reflector':

                    # Add the device and interface to the rr_ips list
                    rr_ips.append({"device": device['name'], "interface": interface['name'], "ip_address": address['address'], "asn": custom_fields['BGP_ASN']})
                elif tag['name']=='route-reflector-client':

                    # Add the device and interface to the rrc_ips list
                    rrc_ips.append({"device": device['name'], "interface": interface['name'], "ip_address": address['address'], "asn": custom_fields['BGP_ASN']})

for rr in rr_ips:
    print(f"route-reflector { rr['device'] } has the following clients:")
    for rrc in rrc_ips:
        config_lines = generate_config_lines(rrc['ip_address'], rrc['device'], rrc['asn'])
        print(config_lines)

for rrc in rrc_ips:
    print(f"route-reflector-client { rrc['device'] } has the following route-reflectors:")
    for rr in rr_ips:
        config_lines = generate_config_lines(rr['ip_address'], rr['device'], rr['asn'])
        print(config_lines)
