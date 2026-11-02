"""External power meter on the outdoor unit: unit conversion and the running threshold."""

# Copyright 2026 JI ENGINEERING
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "power", HERE.parent / "custom_components" / "toshiba_modbus" / "power.py")
power = importlib.util.module_from_spec(spec)
spec.loader.exec_module(power)


def test_watts_from_the_sources_unit():
    assert power.to_watts("2830", "W") == 2830
    assert power.to_watts("0.45", "kW") == 450
    assert power.to_watts("12", None) == 12          # no unit reported: assume watts


def test_unreadable_source_is_unknown_not_zero():
    """A meter that is offline must not read as 'standby' and flip the sensor to off."""
    assert power.to_watts("unavailable", "W") is None
    assert power.to_watts(None, "W") is None
    assert power.to_watts("5", "VA") is None         # unit we cannot convert
    assert power.is_running(None, 100) is None


def test_threshold_is_inclusive():
    assert power.is_running(99.9, 100) is False
    assert power.is_running(100, 100) is True
