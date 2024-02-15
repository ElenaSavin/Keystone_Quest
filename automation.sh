#!/bin/bash

# Path to your values.yaml file
values_file="chart/values.yaml"

# Extract the list of UUIDs into an array
uuids=($(yq e '.uuids[]' $values_file))

# Track the index of the next UUID to use
index=0

# Total number of UUIDs
total_uuids=${#uuids[@]}

while [ "$index" -lt "$total_uuids" ]; do
    # Check for nodes without any running pods
    free_nodes=$(kubectl get nodes --no-headers | grep 'Ready' | awk '{print $1}')
    for node in $free_nodes; do
        # Check if the node is running any jobs
        running_jobs=$(kubectl get pods -n keystone -o wide | grep $node | wc -l)
        if [ "$running_jobs" -eq 0 ]; then
            # If a node is free, trigger the next cronjob
            uuid=${uuids[$index]}
            cronjob_name=$uuid
            kubectl create job --from=cronjob/$cronjob_name $cronjob_name-job -n keystone
            echo "Created job ${uuid}"
            # Increment to use the next UUID
            ((index++))
            # Assuming one job per node at a time, break to re-check node availability
            break
        fi
    done
    # Sleep before checking again to limit API calls
    sleep 5
done
