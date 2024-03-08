# hiermit die seed.iso für vyos ZTP erstellen

# seed-1
seed-1 ist für den ersten router und hat noch dhcp auf dem eth1 (internet-uplink)

# seed-n
seed-n ist für alle weiteren router

im jeweiligen Verzeichnis vor allem die user-data bearbeiten und die eigenen keys hinterlegen!

erstellen dann entweder
für seed-1
mkisofs -joliet -rock -volid "cidata" -output seed-1.iso meta-data user-data network-config

oder für seed-n
mkisofs -joliet -rock -volid "cidata" -output seed-n.iso meta-data user-data network-config

im jeweiligen verzeichnis ausführen und dann die beiden iso-dateien in /var/lib/vz/template/iso ablegen.
