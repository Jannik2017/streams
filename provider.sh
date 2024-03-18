#!/bin/bash

##
## provider.sh erstellt eine Anzahl VMs auf einem Proxmox-Host um ein ISP-Netzwerk zu erstellen.
##

## SSH beschwert sich wenn man die VMs ein paar mal auf- und abbaut wegen der Host-Keys
export ANSIBLE_HOST_KEY_CHECKING=False

## 
## Kommandozeilen-Parameter (unnamed)
## 
## Variablem um die VM-ID zu bauen
node=$1
provider=$2
## soll vorher "abgerissen" werden?
destroy=$3
## aus wievielen Routern soll das Gitter bestehen?
## Vorsicht! Das ansible inventory muss dazu passen!
routers=$4
## nur bestimmte VMs bearbeiten
ansible_limit=$5
## wo liegen die inventories und roles fuer ansible
ansible_folder=$6

## Funktion zum warten auf reboots nach Installation, Update und Config
sleeping ()
{
    for r in $(seq 1 $2)
    do
	while true
	do
	    ansible -i /home/aibix/streams/${ansible_folder}/inventories/inventory$1.yaml p$1r${r}v -m ping -u vyos | grep -q pong && break
	done
	echo "Router ${r} in Betrieb"
    done
}

## 
## VMs entfernen und neu ausrollen
## 
cd ${HOME}/streams/create-vms/create-vms-vyos/

## zuerst entfernen
if [ $destroy == 1 ]
then
    ## wenn NOEXIST==1 dann gibt es keine Config für die angefragte VM
    ## evtl. ist sie auf einem anderen Node im Cluster oder schlicht nicht existent
    NOEXIST=0    
    echo "VMs entfernen"
    for r in $(seq 1 ${routers})
    do
	echo -n "Setze HA-Gruppe P3 fuer VM $r ... "
	sudo ha-manager set vm:${node}0${provider}00${r} --group "P2"
	if [[ $? -eq 0 ]]
	then
	    echo "fertig."
	else
	    NOEXIST=1
	fi

	## VMs bei Bedarf auf diesen Node verschieben um sie zu entfernen
	## ha-manager kann sie m.W. nicht entfernen, daher muss das lokal passieren
	## (auf dem Node auf dem diese Scripte laufen)
	if [[ $NOEXIST == 0 ]]
	then
	    echo -n "Migriere VM $r auf diesen Knoten "
	    while true
	    do
		## sicherstellen dass die VM auf diesem Node ist
		## (sie wird durch Cluster-Regeln nach dem setzen der Gruppe P3 oben automatisch migriert, hier nur warten)
		sleep 1
		output=`sudo ha-manager status | grep ${node}0${provider}00${r}`
		if [[ $? -eq 0 && `echo $output | grep minismox` ]]
		then
		    echo " fertig."
		    break
		else
		    echo -n "."
		fi
	    done

	    echo -n "Entferne VM aus dem ha-manager ... "
	    sudo ha-manager remove vm:${node}0${provider}00${r}
	    if [[ $? -eq 0 ]] ; then echo "fertig." ; fi
	    
	    for j in 0 1
	    do
		echo -n "Entferne Replikation-Job $j ... "
		sudo pvesr delete ${node}0${provider}00${r}-${j}
		if [[ $? -eq 0 ]] ; then echo "fertig" ; fi
	    done
	    
	    echo -n "Warten auf cronjob bis Replikation-Jobs entfernt sind "
	    while true
	    do
		if ! [[ $(sudo pvesr list | grep ^${node}0${provider}00${r}) ]]
		then
		    echo " fertig."
		    break
		fi
		echo -n "."
		sleep 1
	    done
	    sudo qm stop ${node}0${provider}00${r}
	    sudo bash create-vm-vyos.sh -c destroy -n ${node} -p ${provider} -r ${r}
	else
	    if [[ $(sudo qm list | grep ${node}0${provider}00${r}) ]]
	    then
		sudo qm stop ${node}0${provider}00${r} && sudo qm destroy ${node}0${provider}00${r} --purge
	    fi
	fi
    done
fi

#
#create
echo "Erstelle VMs"
for r in $(seq 1 ${routers})
do
    sudo bash create-vm-vyos.sh -c create -n ${node} -p ${provider} -r ${r}
    sudo qm start ${node}0${provider}00${r}
    ssh-keygen -f "/home/aibix/.ssh/known_hosts" -R "10.20.30.${provider}${r}"
done

#sleeping
echo "Warte auf ersten Start"
sleeping $provider $routers

#
# switch back to ansible_folder to update and configure vms
cd ${HOME}/streams/${ansible_folder}

#
#update and reboot
echo "System Upgrade"
ansible-playbook -i inventories/inventory${provider}.yaml vyos_update.yml -e "vyos_version=$(ls -t ${HOME}/streams/${ansible_folder}/vyos-files/ | head -n 1 | sed -e 's/^vyos-//' | sed -e 's/-amd.*$//')" $ansible_limit

#
#reboot (hart; wegen kaputtem cloud-init)
echo "Harter Reboot (initiales Image bleibt beim Herunterfahren haengen)"
for r in $(seq 1 ${routers})
do
    sudo qm reset ${node}0${provider}00${r}
done

#
#sleeping
echo "Warte auf zweiten Start"
sleeping $provider $routers

#
#configuring
echo "Konfiguriere Netzwerk"
ansible-playbook -i inventories/inventory${provider}.yaml setup.yml $ansible_limit

#
#remove cdrom
echo "Entferne seed.iso (cloud-init) CD aus dem Laufwerk"
for r in $(seq 1 ${routers})
do
    sudo qm set ${node}0${provider}00${r} --ide2 media=cdrom,file=none
done

#
#reboot (muss nicht sein, aber mal checken schadet ja nicht)
echo "Warte auf dritten Start"
ansible-playbook -i inventories/inventory${provider}.yaml vyos_reboot.yml $ansible_limit
sleeping $provider $routers

# add replication
for r in $(seq 1 ${routers})
do
    for j in 0 1
    do
	case $j in
	    0)
		sudo pvesr create-local-job ${node}0${provider}00${r}-0 doodlemox --schedule "*/3"
		;;
	    1)
		sudo pvesr create-local-job ${node}0${provider}00${r}-1 minismox --schedule "*/3"
		;;
	esac
    done
done

# add ha
for r in $(seq 1 ${routers})
do
    echo -n "Prüfe ob sync abgeschlossen ist "
    while true
    do
	STATUS1=$(sudo pvesr status --guest ${node}0${provider}00${r} | awk "/${node}0${provider}00${r}-0/ { print \$8 }")
	LAST1=$(sudo pvesr status --guest ${node}0${provider}00${r} | awk "/${node}0${provider}00${r}-0/ { print \$4 }")
	STATUS2=$(sudo pvesr status --guest ${node}0${provider}00${r} | awk "/${node}0${provider}00${r}-1/ { print \$8 }")
	LAST2=$(sudo pvesr status --guest ${node}0${provider}00${r} | awk "/${node}0${provider}00${r}-1/ { print \$4 }")
	if [[ $STATUS1 == "OK" && $LAST1 != "-" && $STATUS2 == "OK" && $LAST2 != "-" ]]
	then
	    echo " fertig"
	    sudo ha-manager add vm:${node}0${provider}00${r} --group "P${provider}" --type vm
	    #sudo ha-manager add vm:${node}0${provider}00${r} --group "P3" --type vm
	    break
	fi
	echo -n "."
	sleep 1
    done
done


echo "Fertig."

