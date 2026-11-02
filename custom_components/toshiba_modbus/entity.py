"""Shared entity base: one device per indoor unit, availability from presence."""

# Copyright 2026 JI ENGINEERING
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from homeassistant.core import Event, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ADAPTER_MODEL, CONF_OUTDOOR_MODEL, CONF_OUTDOOR_SERIAL, DOMAIN, MANUFACTURER, OUTDOOR_NAME
from .coordinator import ToshibaModbusCoordinator


class ToshibaUnitEntity(CoordinatorEntity[ToshibaModbusCoordinator]):
    """Every entity belongs to one indoor unit, which is one device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ToshibaModbusCoordinator, unit: int, key: str) -> None:
        super().__init__(coordinator)
        self._unit = unit
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{unit}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        c = self.coordinator
        return DeviceInfo(
            identifiers={(DOMAIN, f"{c.entry.entry_id}_{self._unit}")},
            name=c.unit_name(self._unit),
            manufacturer=MANUFACTURER,
            model=c.model(self._unit) or ADAPTER_MODEL,
            serial_number=c.serial(self._unit),
            via_device_id=c.hub_device_id,
        )

    @property
    def available(self) -> bool:
        # Nieobecna jednostka zwraca poprawną ramkę zer, nie błąd - bez tego
        # testu encje pokazywałyby 0 °C i tryb "invalid" jako prawdziwe dane.
        return super().available and self.coordinator.present(self._unit)


class ToshibaInterfaceEntity(CoordinatorEntity[ToshibaModbusCoordinator]):
    """Encje samego interfejsu Modbus - nie należą do żadnej jednostki wewnętrznej."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ToshibaModbusCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_iface_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self.coordinator.entry.entry_id)})


class ToshibaOutdoorEntity(CoordinatorEntity[ToshibaModbusCoordinator]):
    """Entity of the outdoor unit (agregat), fed by an external meter on its supply.

    A multisplit has one outdoor unit for several indoor ones, so a meter on its supply
    belongs to none of them. The RAC interface does not report the outdoor unit at all
    (see README, "Hardware notes"), so this device exists only for the meter. It follows
    the meter's own state changes - the poll never touches it - and is available while the
    meter is, not while the Modbus bus answers.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: ToshibaModbusCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_outdoor_{key}"

    def _source(self) -> str | None:
        raise NotImplementedError

    @property
    def device_info(self) -> DeviceInfo:
        c = self.coordinator
        options = c.entry.options
        return DeviceInfo(
            identifiers={(DOMAIN, f"{c.entry.entry_id}_outdoor")},
            name=OUTDOOR_NAME,
            manufacturer=MANUFACTURER,
            model=options.get(CONF_OUTDOOR_MODEL) or "Outdoor unit",
            serial_number=options.get(CONF_OUTDOOR_SERIAL) or None,
            via_device_id=c.hub_device_id,
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if source := self._source():
            @callback
            def _changed(event: Event) -> None:
                self.async_write_ha_state()

            self.async_on_remove(async_track_state_change_event(self.hass, [source], _changed))

    @property
    def available(self) -> bool:
        source = self._source()
        state = self.hass.states.get(source) if source else None
        return state is not None and state.state not in ("unknown", "unavailable")
