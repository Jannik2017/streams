#!/bin/env bash

for i in {0..7}
do
    curl --insecure \
	 -H "Authorization: Token 29807a042ce4bc270bcdc736a1305793d2ee401f" \
	 -H "Content-Type: application/json" -H "Accept: application/json; indent=4" \
	 https://192.168.111.205/api/ipam/prefixes/ \
	 -X POST --data "{\"prefix\": \"2001:470:731b:4${i}00::/56\", \"status\": \"active\", \"tags\": [1], \"tenant\": 1, \"site\": 2}"
done
