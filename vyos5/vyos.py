#!/usr/bin/env python3

import json
from napalm import get_network_driver

driver = get_network_driver('vyos')

vyos_router = driver(
    hostname="10.20.30.22",
    username="vyos",
    password="vyos",
    optional_args={"port": 22},
)

vyos_router.open()
output = vyos_router.get_facts()
print(json.dumps(output, indent=4))

output = vyos_router.get_arp_table()
print(json.dumps(output, indent=4))

vyos_router.close()