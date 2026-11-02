"""Pure helpers for the optional external power measurement (no Home Assistant imports)."""

# Copyright 2026 JI ENGINEERING
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

_TO_WATTS = {"W": 1.0, "kW": 1000.0, "mW": 0.001}


def to_watts(value: object, unit: str | None) -> float | None:
    """A source reading as watts, or None when it is not a number or the unit is unknown."""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    factor = _TO_WATTS.get(unit or "W")
    return None if factor is None else number * factor


def is_running(watts: float | None, threshold: float) -> bool | None:
    """Whether the unit draws more than standby. None while the reading is unknown."""
    return None if watts is None else watts >= threshold
