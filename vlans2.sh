#! /bin/bash
#
# beigesteuert von maschmakai

TOTALROUTER=$1
TOTALROWS=$2

RPR=$[${TOTALROUTER}/${TOTALROWS}] #get routers per row


for ROW in $(seq 1 $TOTALROWS)
do
    FIRSTROUTER=$[$[${ROW}*${RPR}]-$[${RPR}-1]]
    LASTROUTER=$[${ROW}*${RPR}]

    for ROUTER in $(seq $FIRSTROUTER $LASTROUTER)
    do

	if [ "$ROUTER" == "$FIRSTROUTER" ]
        then
            echo "R${ROUTER}:net1:$((ROUTER+100))"
        else
            echo "R${ROUTER}:net1:$((ROUTER-1))$ROUTER"
        fi

	if [ "$ROW" == "1" ]
	then
	    echo "R${ROUTER}:net2:$((ROUTER+200))"
	else
	    echo "R${ROUTER}:net2:$((ROUTER-RPR))$ROUTER"
	fi

	if [ "$ROUTER" == "$LASTROUTER" ]
        then
            echo "R${ROUTER}:net3:$((ROUTER+300))"
        else
            echo "R${ROUTER}:net3:$ROUTER$((ROUTER+1))"
        fi

	if [ "$ROW" == "$TOTALROWS" ]
        then
            echo "R${ROUTER}:net4:$((ROUTER+400))"
        else
            echo "R${ROUTER}:net4:$ROUTER$((ROUTER+RPR))"
        fi
    done
done

