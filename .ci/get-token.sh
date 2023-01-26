#!/usr/bin/env bash

set -e
resp=$(curl -A 'ipxe-ca' --header 'Authorization: Bearer '"$TTS_TOKEN"'' -X POST https://tt-service.hetzner.cloud/token -o resp.json)
if grep -q token "resp.json"
then
    token=$(cat resp.json | jq -r '.token')
    echo $token
else
    exit 1
fi
