#!/usr/bin/env bash

DEV_ID="unique_device_id"
TS=$(date +%s)
MINUTE=$(date +%M)
TOTAL_FLOW=${2:-100}
CAPACITY=${3:-4000}
PEAK_FLOW=${2:-4}


if [[ $1 == "stats" ]]; then
    curl -i \
        -X POST "http://erieconnect.eriewatertreatment.com/api/device/v1/water_softener/stats" -H "Content-Type: application/json" \
        -d '{"id":"'$DEV_ID'","content":{"ts":'$TS',"payload":{"total_flow":'$TOTAL_FLOW',"capacity_remaining":'$CAPACITY',"state":1,"cycle_timer":0,"brine_fill_seconds":518,"days_maintenance":32,"salt_alarm_count":4,"maintenance_time":24,"firmware_msg":"FW_STRING","pn_msg":"PING_STRING","minute":'$MINUTE'}},"t":"SOMETHING"}'

elif [[ $1 == "flow" ]]; then
    curl -i \
        -X POST "http://erieconnect.eriewatertreatment.com/api/device/v1/water_softener/flow" -H "Content-Type: application/json" \
        -d '{"id":"'$DEV_ID'","content":{"ts":'$TS',"payload":{"peak_flow_rate":'$PEAK_FLOW'}},"t":"SOMETHING"}'

else
    echo 'One of "stats", "flow" required as first argument.'
fi
