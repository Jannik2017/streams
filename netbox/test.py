#!/usr/bin/env python3

from netbox import NetBox
netbox = NetBox(host='192.168.111.205', port=443, use_ssl=True, auth_token='29807a042ce4bc270bcdc736a1305793d2ee401f')

for prefix in netbox.ipam.get_ip_prefixes():

    if len(prefix['tags']) > 0:
        print(f'prefix { prefix["prefix"] } has tags: { ",".join([tag["name"] for tag in prefix["tags"]]) }')
    else:
        print(f'prefix { prefix["prefix"] } has no tags')
        
