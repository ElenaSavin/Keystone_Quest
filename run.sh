#!/bin/bash

export file=$1
python src/main.py -f files --filename "${file}" -d true

if [[ -f "${file}_output.csv" ]]; then
    oci os object put --bucket-name Keystone-Quest-Outcome --file "${file}_output.csv"
    oci os object put --bucket-name Keystone-Quest-Outcome --file "${file}_summery.csv"
fi
