from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
    RestoreSensor,
)

from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo

from homeassistant.const import (
    UnitOfVolumeFlowRate,
    UnitOfVolume,
    UnitOfTime,
)

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .signals import (
    SIGNAL_DEVICE_ID,
    SIGNAL_STATE,
    SIGNAL_BRINE_FILL_SECONDS,
    SIGNAL_CAPACITY_REMAINING,
    SIGNAL_CYCLE_TIMER,
    SIGNAL_DAYS_MAINTENANCE,
    SIGNAL_MAINTENANCE_TIME,
    SIGNAL_PEAK_FLOW_RATE,
    SIGNAL_SALT_ALARM_COUNT,
    SIGNAL_TOTAL_FLOW,
)


from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
)


import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    known_devices = set()

    async def _device_discovered(device_id: str) -> None:
        if (
            not device_id
            or device_id in known_devices
        ):
            return

        known_devices.add(device_id)

        async_add_entities([
            # Operational state
            BinarySensor(
                device_id = device_id,
                sensor_id = "state",
                signal    = SIGNAL_STATE,

                device_class = BinarySensorDeviceClass.RUNNING,
            ),

            # Total flow (L).
            RestoredIntSensor(
                device_id = device_id,
                sensor_id = "total_flow",
                signal    = SIGNAL_TOTAL_FLOW,

                state_class  = SensorStateClass.TOTAL_INCREASING,
                device_class = SensorDeviceClass.WATER,
                native_unit  = UnitOfVolume.LITERS,
                icon         = "mdi:water",
            ),

            # Capacity remaining (L).
            IntSensor(
                device_id = device_id,
                sensor_id = "capacity_remaining",
                signal    = SIGNAL_CAPACITY_REMAINING,

                state_class  = SensorStateClass.MEASUREMENT,
                device_class = SensorDeviceClass.VOLUME_STORAGE,
                native_unit  = UnitOfVolume.LITERS,
                icon         = "mdi:storage-tank",
            ),

            # Brine fill (s).
            IntSensor(
                device_id = device_id,
                sensor_id = "brine_fill_seconds",
                signal    = SIGNAL_BRINE_FILL_SECONDS,

                state_class  = SensorStateClass.MEASUREMENT,
                device_class = SensorDeviceClass.DURATION,
                native_unit  = UnitOfTime.SECONDS,
            ),

            # Days maintenance (day).
            IntSensor(
                device_id = device_id,
                sensor_id = "days_maintenance",
                signal    = SIGNAL_DAYS_MAINTENANCE,

                state_class  = SensorStateClass.MEASUREMENT,
                device_class = SensorDeviceClass.DURATION,
                native_unit  = UnitOfTime.DAYS,
            ),

            # Peak flow rate (L/min).
            IntSensor(
                device_id = device_id,
                sensor_id = "peak_flow_rate",
                signal    = SIGNAL_PEAK_FLOW_RATE,

                state_class  = SensorStateClass.MEASUREMENT,
                device_class = SensorDeviceClass.VOLUME_FLOW_RATE,
                native_unit  = UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
                icon         = "mdi:pipe-valve",
                initial      = 0
            ),

            # Cycle timer (?).
            IntSensor(
                device_id = device_id,
                sensor_id = "cycle_timer",
                signal    = SIGNAL_CYCLE_TIMER,

                state_class = SensorStateClass.MEASUREMENT,
            ),

            # Salt alarm count (?).
            IntSensor(
                device_id = device_id,
                sensor_id = "salt_alarm_count",
                signal    = SIGNAL_SALT_ALARM_COUNT,

                state_class = SensorStateClass.MEASUREMENT,
            ),

            # Maintenance time (?).
            IntSensor(
                device_id = device_id,
                sensor_id = "maintenance_time",
                signal    = SIGNAL_MAINTENANCE_TIME,

                state_class = SensorStateClass.MEASUREMENT,
            ),
        ])


    existing_devices = device_registry.async_entries_for_config_entry(
        device_registry.async_get(hass),
        config_entry.entry_id,
    )

    for device in existing_devices:
        for identifier in device.identifiers:
            if (identifier[0] == DOMAIN):
                _LOGGER.info("Adding known device %s", identifier[1])
                await _device_discovered(identifier[1])

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            SIGNAL_DEVICE_ID,
            _device_discovered,
        )
    )


class BinarySensor(BinarySensorEntity):
    my_signal = ""

    _attr_has_entity_name = True


    def __init__(
        self,
        device_id: str,
        sensor_id: str,
        signal: str,

        state_class  = None,
        device_class = None,
        native_unit  = None,
        icon: str    = None,
    ) -> None:
        self.my_signal = signal

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            model="IQ Soft",
            manufacturer="Pentair",
            name="Pentair IQ Soft Cabinet Softener",
        )

        self._attr_unique_id                  = f"{device_id}_{sensor_id}"
        self._attr_translation_key            = sensor_id
        self._attr_state_class                = state_class
        self._attr_device_class               = device_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_icon                       = icon


    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, self.my_signal, self._handle_signal)
        )


    @callback
    def _handle_signal(self, value: bool) -> None:
        self._attr_is_on = value
        self.async_write_ha_state()



class IntSensor(SensorEntity):
    my_signal = ""

    _attr_has_entity_name             = True
    _attr_suggested_display_precision = 0


    def __init__(
        self,
        device_id: str,
        sensor_id: str,
        signal: str,

        state_class  = None,
        device_class = None,
        native_unit  = None,
        icon: str    = None,
        initial      = None,
    ) -> None:
        self.my_signal = signal

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            model="IQ Soft",
            manufacturer="Pentair",
            name="Pentair IQ Soft Cabinet Softener",
        )

        self._attr_unique_id                  = f"{device_id}_{sensor_id}"
        self._attr_translation_key            = sensor_id
        self._attr_state_class                = state_class
        self._attr_device_class               = device_class
        self._attr_native_unit_of_measurement = native_unit
        self._attr_icon                       = icon

        if initial is not None:
            self._attr_native_value = initial


    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        self.async_on_remove(
            async_dispatcher_connect(self.hass, self.my_signal, self._handle_signal)
        )


    @callback
    def _handle_signal(self, value: int) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()



class RestoredIntSensor(RestoreSensor, IntSensor):
    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        last_data = await self.async_get_last_sensor_data()

        if last_data is not None:
            self._attr_native_value = last_data.native_value
