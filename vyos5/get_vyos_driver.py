from napalm import get_network_driver

drivers = get_network_driver("vyos")
print(drivers)