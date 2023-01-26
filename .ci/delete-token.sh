#!/usr/bin/env bash

set -e
token=$1
curl -A 'ipxe-ca' --header 'Authorization: Bearer '"$TTS_TOKEN"'' -X DELETE https://tt-service.hetzner.cloud/token?token=''"$token"''
