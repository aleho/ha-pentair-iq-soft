# Home Assistant Integration for Pentair IQ Soft water softeners

[![Marketplace Validation](https://github.com/aleho/ha-pentair-iq-soft/actions/workflows/validate.yml/badge.svg)](https://github.com/aleho/ha-pentair-iq-soft/actions/workflows/validate.yml)


# Installation

Add a custom repository and install the integration.

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=aleho&repository=ha-pentair-iq-soft&category=integration) 


After installing, add the integration. Entities will be created as soon as data
arrives.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=pentair_iq_soft)


## Setup

1. Use the setup and app (ConnectMySoftener) to configure your water softener to
   push data to the API (http://erieconnect.eriewatertreatment.com).
2. Add a DNS entry for `erieconnect.eriewatertreatment.com` in the network the
   softener is configured to use, pointing to the IP address of your local HA
   server. 
