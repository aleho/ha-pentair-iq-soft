import logging
from collections.abc import Callable, Iterable
from typing import Self, override

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .signals import SIGNAL_DEVICE_ID

type TSignalValue = int | bool | None

_LOGGER = logging.getLogger(__name__)


class PentairEntityDescription(EntityDescription):
    has_entity_name = True
    signal: str
    initial: TSignalValue = None
    value_handler: Callable[[TSignalValue], TSignalValue] | None = None


class PentairEntity(Entity):
    entity_description: PentairEntityDescription
    my_signal = ""

    def __init__(
        self,
        description: PentairEntityDescription,
        device_id: str,
    ) -> None:
        self.entity_description = description
        self.my_signal = description.signal

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            model="IQ Soft",
            manufacturer="Pentair",
            name="Pentair IQ Soft Cabinet Softener",
        )

        self._attr_unique_id = f"{device_id}_{description.key}"

        if description.initial is not None:
            self._attr_native_value = description.initial

    @override
    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self.my_signal, self._handle_signal_callback
            )
        )

    @callback
    def _handle_signal_callback(self, value: TSignalValue) -> None:
        if self.entity_description.value_handler is not None:
            value = self.entity_description.value_handler(value)

        self._handle_signal(value)
        self.async_write_ha_state()

    def _handle_signal(self, value: TSignalValue) -> None:
        """Signal handler to be implemented by children."""

    @classmethod
    def from_list(
        cls,
        device_id: str,
        descriptions: tuple[PentairEntityDescription, ...],
    ) -> Iterable[Self]:
        entities = []

        for description in descriptions:
            entities.append(cls(description=description, device_id=device_id))

        return entities


async def connect_platform(
    entities_callable: (Callable[[str], Iterable[PentairEntity]]),
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    known_devices = set()

    async def _device_discovered(device_id: str) -> None:
        if not device_id or device_id in known_devices:
            return

        known_devices.add(device_id)

        async_add_entities(entities_callable(device_id))

    existing_devices = device_registry.async_entries_for_config_entry(
        device_registry.async_get(hass),
        config_entry.entry_id,
    )

    for device in existing_devices:
        for identifier in device.identifiers:
            if identifier[0] == DOMAIN:
                _LOGGER.info("Adding known device %s", identifier[1])
                await _device_discovered(identifier[1])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            SIGNAL_DEVICE_ID,
            _device_discovered,
        )
    )
