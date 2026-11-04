import logging
from http import HTTPStatus

import aiohttp
import dns.resolver
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN
from .signals import (
    SIGNAL_BRINE_FILL_SECONDS,
    SIGNAL_CAPACITY_REMAINING,
    SIGNAL_CYCLE_TIMER,
    SIGNAL_DAYS_MAINTENANCE,
    SIGNAL_DEVICE_ID,
    SIGNAL_MAINTENANCE_TIME,
    SIGNAL_PEAK_FLOW_RATE,
    SIGNAL_SALT_ALARM_COUNT,
    SIGNAL_STATE,
    SIGNAL_TOTAL_FLOW,
)

URL_BASE = "/api/device/v1/water_softener"
_LOGGER = logging.getLogger(__name__)


class BaseView(HomeAssistantView):
    def _log(self, message, *args) -> None:
        _LOGGER.error("[%s] " + message, self.url, *args)

    def _debug(self, message, *args) -> None:
        _LOGGER.debug("[%s] " + message, self.url, *args)

    async def _parse_request(self, request: web.Request) -> tuple[dict, dict]:
        data = await request.json()

        if "content" not in data:
            return data, {}

        if "payload" not in data["content"]:
            return data, {}

        return data, data["content"]["payload"]

    async def post(self, request: web.Request) -> web.Response:
        try:
            hass = request.app["hass"]
            (data, payload) = await self._parse_request(request)

            self._debug("payload: %s", payload)

            if "id" in data:
                hass.add_job(
                    async_dispatcher_send,
                    hass,
                    SIGNAL_DEVICE_ID,
                    data["id"],
                )

            self._handle_payload(payload, hass)

            return await self._handle_response(payload, hass)

        except (ValueError, TypeError) as err:
            self._log("%s", err)
            return web.Response(status=HTTPStatus.BAD_REQUEST)

        except Exception as err:
            self._log("%s", err)
            return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_payload(self, payload: dict, hass: HomeAssistant) -> None:
        """Handles the actual API payload"""
        pass

    async def _handle_response(
        self, payload: dict, hass: HomeAssistant
    ) -> web.Response:
        return web.Response(status=HTTPStatus.OK)


class StatsView(BaseView):
    requires_auth = False
    url = URL_BASE + "/stats"
    name = f"api:{DOMAIN}:stats"

    def _handle_payload(self, payload: dict, hass) -> None:
        if "state" in payload:
            async_dispatcher_send(
                hass, SIGNAL_STATE, True if payload["state"] == 1 else False
            )

        if "total_flow" in payload:
            async_dispatcher_send(hass, SIGNAL_TOTAL_FLOW, int(payload["total_flow"]))

        if "capacity_remaining" in payload:
            async_dispatcher_send(
                hass, SIGNAL_CAPACITY_REMAINING, int(payload["capacity_remaining"])
            )

        if "cycle_timer" in payload:
            async_dispatcher_send(hass, SIGNAL_CYCLE_TIMER, int(payload["cycle_timer"]))

        if "brine_fill_seconds" in payload:
            async_dispatcher_send(
                hass, SIGNAL_BRINE_FILL_SECONDS, int(payload["brine_fill_seconds"])
            )

        if "days_maintenance" in payload:
            async_dispatcher_send(
                hass, SIGNAL_DAYS_MAINTENANCE, int(payload["days_maintenance"])
            )

        if "salt_alarm_count" in payload:
            async_dispatcher_send(
                hass, SIGNAL_SALT_ALARM_COUNT, int(payload["salt_alarm_count"])
            )

        if "maintenance_time" in payload:
            async_dispatcher_send(
                hass, SIGNAL_MAINTENANCE_TIME, int(payload["maintenance_time"])
            )


class CurrentFlowView(BaseView):
    requires_auth = False
    url = URL_BASE + "/flow"
    name = f"api:{DOMAIN}:flow"

    def _handle_payload(self, payload: dict, hass: HomeAssistant) -> None:
        if "peak_flow_rate" in payload:
            async_dispatcher_send(
                hass, SIGNAL_PEAK_FLOW_RATE, int(payload["peak_flow_rate"])
            )


class GetTimeView(BaseView):
    requires_auth = False
    url = URL_BASE + "/get_time"
    name = f"api:{DOMAIN}:get_time"

    async def _parse_request(self, request: web.Request) -> tuple[dict, dict]:
        post = await request.post()

        if "id" not in post:
            return {}, {}

        data = {
            "id": post["id"],
        }

        return data, data

    async def _handle_response(
        self, payload: dict, hass: HomeAssistant
    ) -> web.Response:
        if "id" not in payload:
            return web.Response(status=HTTPStatus.BAD_REQUEST)

        hostname = "erieconnect.eriewatertreatment.com"

        try:
            server_ip = await hass.async_add_executor_job(
                lambda: self._resolve_dns(hostname)
            )
        except dns.resolver.NoAnswer:
            self._log("could not query DNS")
            return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        session = async_get_clientsession(hass)

        self._debug("resolved upstream server IP %s", server_ip)

        headers = {
            "Host": hostname,
            "User-Agent": "EIQ_AC/1.5.0",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            async with session.post(
                url=f"http://{server_ip}{self.url}",
                data=f"id={payload['id']}",
                headers=headers,
                timeout=10,
            ) as response:
                self._debug("upstream response: %s", await response.text())
                self._debug("upstream headers: %s", response.headers)

                if response.status != HTTPStatus.OK:
                    self._log(
                        "unexpected upstream response, status=%s", response.status
                    )
                    return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

                return web.Response(
                    status=HTTPStatus.OK,
                    headers={"Content-Type": "application/json"},
                    text=await response.text(),
                )

        except aiohttp.ClientError as err:
            self._log("request failed: %s", err)
            return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _resolve_dns(self, hostname: str) -> str:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["8.8.8.8"]

        return resolver.resolve(hostname, "A").rrset[0].to_text()
