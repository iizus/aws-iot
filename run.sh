#!/bin/bash

read_config () {
    echo `cat config.json` | jq -r $1
}

endpoint=$(read_config '.endpoint')
CA=$(read_config '.certs.CA')

python code/fleetprovisioning.py \
    --endpoint $endpoint \
    --root-ca $CA \
    --cert certs/claim.pem.crt \
    --key certs/claim.pem.key \
    --templateName ec2 \
    --templateParameters "{}"

python code/pubsub.py \
    --endpoint $endpoint \
    --root-ca $CA \
    --cert certs/client.pem.crt \
    --key certs/client.pem.key \
    --count 0