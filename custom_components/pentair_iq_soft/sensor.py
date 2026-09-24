from dataclasses import dataclass
from typing import override

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfTime,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import (
    PentairEntity,
    PentairEntityDescription,
    TSignalValue,
    connect_platform,
)
from .signals import (
    SIGNAL_BRINE_FILL_SECONDS,
    SIGNAL_CAPACITY_REMAINING,
    SIGNAL_CYCLE_TIMER,
    SIGNAL_DAYS_MAINTENANCE,
    SIGNAL_MAINTENANCE_TIME,
    SIGNAL_PEAK_FLOW_RATE,
    SIGNAL_SALT_ALARM_COUNT,
    SIGNAL_TOTAL_FLOW,
)


@dataclass(frozen=True, kw_only=True)
class IntSensorDescription(PentairEntityDescription, SensorEntityDescription):
    """Describes an int sensor."""

    suggested_display_precision = 0


class IntSensor(PentairEntity, SensorEntity):
    entity_description: IntSensorDescription

    @override
    def _handle_signal(self, value: TSignalValue) -> None:
        if isinstance(value, int):
            self._attr_native_value = value
        else:
            self._attr_native_value = None


class RestoredIntSensor(IntSensor, RestoreSensor):
    entity_description: IntSensorDescription

    @override
    async def async_added_to_hass(self) -> None:
        last_data = await self.async_get_last_sensor_data()

        if last_data is not None:
            self._attr_native_value = last_data.native_value


_RESTORED_INT_SENSORS: tuple[IntSensorDescription, ...] = (
    # Total flow (L).
    IntSensorDescription(
        key="total_flow",
        translation_key="total_flow",
        signal=SIGNAL_TOTAL_FLOW,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        icon="mdi:water",
    ),
)


_INT_SENSORS: tuple[IntSensorDescription, ...] = (
    # Capacity remaining (L).
    IntSensorDescription(
        key="capacity_remaining",
        translation_key="capacity_remaining",
        signal=SIGNAL_CAPACITY_REMAINING,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_STORAGE,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        icon="mdi:storage-tank",
    ),
    # Brine fill (s).
    IntSensorDescription(
        key="brine_fill_seconds",
        translation_key="brine_fill_seconds",
        signal=SIGNAL_BRINE_FILL_SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    # Days maintenance (day).
    IntSensorDescription(
        key="days_maintenance",
        translation_key="days_maintenance",
        signal=SIGNAL_DAYS_MAINTENANCE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.DAYS,
    ),
    # Peak flow rate (L/min).
    IntSensorDescription(
        key="peak_flow_rate",
        translation_key="peak_flow_rate",
        signal=SIGNAL_PEAK_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        icon="mdi:pipe-valve",
        initial=0,
    ),
    # Cycle timer (?).
    IntSensorDescription(
        key="cycle_timer",
        translation_key="cycle_timer",
        signal=SIGNAL_CYCLE_TIMER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Salt alarm count.
    IntSensorDescription(
        key="salt_alarm_count",
        translation_key="salt_alarm_count",
        signal=SIGNAL_SALT_ALARM_COUNT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # Maintenance time (?).
    IntSensorDescription(
        key="maintenance_time",
        translation_key="maintenance_time",
        signal=SIGNAL_MAINTENANCE_TIME,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await connect_platform(
        lambda device_id: (
            *RestoredIntSensor.from_list(device_id, _RESTORED_INT_SENSORS),
            *IntSensor.from_list(device_id, _INT_SENSORS),
        ),
        hass,
        config_entry,
        async_add_entities,
    )
