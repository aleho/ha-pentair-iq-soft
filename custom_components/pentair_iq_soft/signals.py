from .const import DOMAIN


# Sensor setup
SIGNAL_DEVICE_ID = f"{DOMAIN}.device_id"

# Binary
SIGNAL_STATE = f"{DOMAIN}.state"

# Integer
SIGNAL_TOTAL_FLOW         = f"{DOMAIN}.total_flow"
SIGNAL_CAPACITY_REMAINING = f"{DOMAIN}.capacity_remaining"
SIGNAL_CYCLE_TIMER        = f"{DOMAIN}.cycle_timer"
SIGNAL_BRINE_FILL_SECONDS = f"{DOMAIN}.brine_fill_seconds"
SIGNAL_DAYS_MAINTENANCE   = f"{DOMAIN}.days_maintenance"
SIGNAL_SALT_ALARM_COUNT   = f"{DOMAIN}.salt_alarm_count"
SIGNAL_MAINTENANCE_TIME   = f"{DOMAIN}.maintenance_time"
SIGNAL_PEAK_FLOW_RATE     = f"{DOMAIN}.peak_flow_rate"
