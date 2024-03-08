for r in 1
do
    echo "1. $$8, 2. \$8"
    echo -n "Prüfe ob sync abgeschlossen ist "
    while true
    do
	STATUS1=`sudo pvesr status --guest 101001 | awk '/101001-0/ { print $8 }'`
	LAST1=`sudo pvesr status --guest 101001 | awk '/101001-0/ { print $4 }'`
	STATUS2=`sudo pvesr status --guest 101001 | awk '/101001-1/ { print $8 }'`
	LAST2=`sudo pvesr status --guest 101001 | awk '/101001-1/ { print $4 }'`
	echo "$STATUS1 $LAST1 ; $STATUS2 $LAST2"
	if [[ $STATUS1 == "OK" && $LAST1 != "-" && $STATUS2 == "OK" && $LAST2 != "-" ]]
	then
	    echo " fertig"
	    #sudo ha-manager add vm:101001 --group "P${provider}" --type vm
	    #sudo ha-manager add vm:101001 --group "P3" --type vm
	    break
	fi
	echo -n "."
	sleep 1
    done
done
