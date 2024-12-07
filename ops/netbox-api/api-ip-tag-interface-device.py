import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

netbox_url = "https://192.168.111.8"
auth_token = "584149a859ea8e7a7f5e2d610c7235a3e2d2460c"
tag_names = ["route-reflector-client", "route-reflector"]
isp_names = ["isp1", "isp2", "isp3"]

for tag_name in tag_names:
    for isp_name in isp_names:
        response = requests.get(f"{netbox_url}/api/ipam/ip-addresses/?tag={tag_name}&tag={isp_name}", headers={
            "Authorization": f"Token {auth_token}",
            "Content-Type": "application/json"},
            verify=False)

        if response.status_code == 200:
            ip_address_data = response.json()
            for ip in ip_address_data["results"]:
                print(f"Ip Address: {ip['address']}; Interface: {ip['assigned_object']['name']}; Device: {ip['assigned_object']['device']['name']}; isp: {isp_name}; config_variant: {tag_name}")

        else:
            print("Failed to retrieve IP addresses")
            exit()
