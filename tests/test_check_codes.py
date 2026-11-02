"""Check codes: the tables come from the service manual (section 9-3) and must stay usable."""

# Copyright 2026 JI ENGINEERING
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "registers", HERE.parent / "custom_components" / "toshiba_modbus" / "registers.py")
reg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reg)


def test_no_error_is_not_looked_up():
    assert reg.check_code_text(0) == reg.NO_ERROR


def test_residential_codes_use_the_0x40xx_words_of_the_manual():
    assert reg.check_code_text(0x4019) == "19: TD sensor (Discharge pipe temperature sensor) error"
    assert reg.check_code_text(0x401F) == "1F: Compressor break down"
    assert all(0x4000 <= code <= 0x40FF for code in reg.CHECK_CODES_RESIDENTIAL)


def test_light_commercial_codes_are_a_separate_range():
    assert reg.check_code_text(0x81) == "H01: Compressor break down"
    assert reg.check_code_text(0xE3) == "P03: Discharge temp. TD1 error"
    assert not set(reg.CHECK_CODES_RESIDENTIAL) & set(reg.CHECK_CODES_LIGHT_COMMERCIAL)


def test_low_byte_of_a_residential_code_still_resolves():
    """0.x keyed its table by 0x04, 0x07 ...; a unit reporting the low byte keeps working."""
    assert reg.check_code_text(0x1B) == reg.check_code_text(0x401B)


def test_a_code_missing_from_the_manual_is_shown_raw():
    assert reg.check_code_text(0x1234) == "0x1234"
    assert reg.check_code_info(0x1234) is None


def test_every_entry_has_a_shown_code_and_a_description():
    for table in (reg.CHECK_CODES_RESIDENTIAL, reg.CHECK_CODES_LIGHT_COMMERCIAL):
        for code, (shown, text) in table.items():
            assert shown and text.strip(), hex(code)
            assert text == text.strip() and "  " not in text, hex(code)
