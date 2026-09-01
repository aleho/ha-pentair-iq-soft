# Home Assistant Integration for Pentair IQ Soft water softeners

# Installation

This integration is best installed using [HACS](https://hacs.xyz/). 

After installing, add the integration. Entities will be created as soon as data
arrives.

## Setup

1. Use the setup and app (ConnectMySoftener) to configure your water softener to
   push data to the API (http://erieconnect.eriewatertreatment.com).
2. Add a DNS entry for `erieconnect.eriewatertreatment.com` in the network the
   softener is configured to use, pointing to the IP address of your local HA
   server. 
