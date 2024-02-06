#!/bin/bash

python src/main.py -f files --filename "${FILE_ID}" -d true

tail -n 2 proccess.log | grep -oP 'Total runtime: \K\d+\.\d+' > ${FILE_ID}_runtime.txt
if [[ -f "${FILE_PATH}/${FILE_ID}_output.csv" ]]; then
    oci os object put --bucket-name Keystone-Quest-Outcome --file "${FILE_PATH}/${FILE_ID}_output.csv"
    oci os object put --bucket-name Keystone-Quest-Outcome --file "${FILE_PATH}/${FILE_ID}_summary.csv"
    oci os object put --bucket-name Keystone-Quest-Outcome --file  ${FILE_ID}_runtime.txt
else
    echo "nothing to push"
fi
