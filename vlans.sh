#!/bin/env bash

routers=$1
rows=$2
vmidbase=10100


for row in {1..$rows}
do
    anfang=$((routers/rows+1))
    ende=$((routers/rows))

    for i in $(eval echo "{1..$ende}")
    do
	if [ $i -gt 1 ]
	then
	    echo "$vmidbase$i:net1:$((i-1))$i"
	fi

	if [ $i -lt 4 ]
	then
	    echo "$vmidbase$i:net3:$i$((i+1))"
	fi

	echo "$vmidbase$i:net4:$((i+4))$i"
    done

    for i in $(eval echo "{$anfang..$routers}")
    do
	if [ $i -gt 5 ]
	then
	    echo "$vmidbase$i:net1:$((i-1))$i"
	fi

	if [ $i -lt 8 ]
	then
       	    echo "$vmidbase$i:net3:$i$((i+1))"
	fi

	echo "$vmidbase$i:net2:$((i-4))$i"
    done
done
