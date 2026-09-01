from typing import (
    Any,
    cast,
)

import voluptuous as vol

from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)


from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    CONF_DEVICE_NAME_DEFAULT,
)


class PentairIqSoftConfigFlow(SchemaConfigFlowHandler, domain=DOMAIN):
    VERSION = 0
    MINOR_VERSION = 1

    config_flow = {
        "user": SchemaFlowFormStep(
            schema = vol.Schema({}),
        ),
    }

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        return "Pentair IQ Soft"
