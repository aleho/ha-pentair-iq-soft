import logging
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.dispatcher import async_dispatcher_send
from http import HTTPStatus

from .signals import (
    SIGNAL_DEVICE_ID,
    SIGNAL_STATE,
    SIGNAL_TOTAL_FLOW,
    SIGNAL_CAPACITY_REMAINING,
    SIGNAL_CYCLE_TIMER,
    SIGNAL_BRINE_FILL_SECONDS,
    SIGNAL_DAYS_MAINTENANCE,
    SIGNAL_SALT_ALARM_COUNT,
    SIGNAL_MAINTENANCE_TIME,
    SIGNAL_PEAK_FLOW_RATE,
)

from .const import DOMAIN

URL_BASE = "/api/device/v1/water_softener"

class BaseView(HomeAssistantView):
    async def _parsePayload(self, data: dict) -> dict:
        if not "content" in data:
            return {}

        if not "payload" in data["content"]:
            return {}

        return data["content"]["payload"]

    async def post(self, request: web.Request) -> web.Response:
        logger = logging.getLogger(__name__)

        try:
            hass = request.app["hass"]
            data = await request.json()

            if "id" in data:
                hass.add_job(
                    async_dispatcher_send,
                    hass,
                    SIGNAL_DEVICE_ID,
                    data["id"],
                )

            payload = await self._parsePayload(data)
            logger.debug("[%s] payload: %s", self.url, payload)

            self._handlePayload(payload, hass)

            return web.Response(status = HTTPStatus.OK, text = "OK")


        except (ValueError, TypeError) as err:
            logger.error("[%s] %s", self.url, err)
            return web.Response(status = HTTPStatus.BAD_REQUEST, text = "Invalid payload")

        except Exception as err:
            logger.error("[%s] %s", self.url, err)
            return web.Response(status = HTTPStatus.INTERNAL_SERVER_ERROR, text = "Internal Error")


    def _handlePayload(self, payload: dict, hass) -> None:
        """Handles the actual API payload"""
        pass



class StatsView(BaseView):
    requires_auth = False
    url           = URL_BASE + "/stats"
    name          = f"api:{DOMAIN}:stats"

    def _handlePayload(self, payload: dict, hass) -> None:
        if "state" in payload:
            async_dispatcher_send(hass, SIGNAL_STATE, True if payload["state"] == 1 else False)

        if "total_flow" in payload:
            async_dispatcher_send(hass, SIGNAL_TOTAL_FLOW, int(payload["total_flow"]))

        if "capacity_remaining" in payload:
            async_dispatcher_send(hass, SIGNAL_CAPACITY_REMAINING, int(payload["capacity_remaining"]))

        if "cycle_timer" in payload:
            async_dispatcher_send(hass, SIGNAL_CYCLE_TIMER, int(payload["cycle_timer"]))

        if "brine_fill_seconds" in payload:
            async_dispatcher_send(hass, SIGNAL_BRINE_FILL_SECONDS, int(payload["brine_fill_seconds"]))

        if "days_maintenance" in payload:
            async_dispatcher_send(hass, SIGNAL_DAYS_MAINTENANCE, int(payload["days_maintenance"]))

        if "salt_alarm_count" in payload:
            async_dispatcher_send(hass, SIGNAL_SALT_ALARM_COUNT, int(payload["salt_alarm_count"]))

        if "maintenance_time" in payload:
            async_dispatcher_send(hass, SIGNAL_MAINTENANCE_TIME, int(payload["maintenance_time"]))


class CurrentFlowView(BaseView):
    requires_auth = False
    url           = URL_BASE + "/flow"
    name          = f"api:{DOMAIN}:flow"

    def _handlePayload(self, payload: dict, hass) -> None:
        if "peak_flow_rate" in payload:
            async_dispatcher_send(hass, SIGNAL_PEAK_FLOW_RATE, int(payload["peak_flow_rate"]))
