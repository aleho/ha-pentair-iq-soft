from dataclasses import dataclass
from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import (
    PentairEntity,
    PentairEntityDescription,
    TSignalValue,
    connect_platform,
)
from .signals import (
    SIGNAL_STATE,
)


@dataclass(frozen=True, kw_only=True)
class BinarySensorDescription(PentairEntityDescription, BinarySensorEntityDescription):
    """Describes a binary sensor entity."""


class BinarySensor(PentairEntity, BinarySensorEntity):
    entity_description: BinarySensorDescription

    @override
    def _handle_signal(self, value: TSignalValue) -> None:
        if isinstance(value, bool):
            self._attr_is_on = value
        else:
            self._attr_is_on = False


SENSORS = (
    # Operational state
    BinarySensorDescription(
        key="state",
        translation_key="state",
        signal=SIGNAL_STATE,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await connect_platform(
        lambda device_id: BinarySensor.from_list(device_id, SENSORS),
        hass,
        config_entry,
        async_add_entities,
    )
