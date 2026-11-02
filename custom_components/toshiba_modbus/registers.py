"""Register map for the Toshiba BMS-IFMB1280U-E Modbus interface.

Source: Service/Specifications Manual FILE No. A10-2103-7, Revision 7 (05.2024),
chapter 7 "Address assignment table" and 3-7 "List of functions for Room Air
Conditioner TU2C-LINK Interface (RAC)".

Wire addresses are documentation numbers minus the space offset:
    coil     = number - 1
    discrete = number - 10001
    input    = number - 30001
    holding  = number - 40001

The stride between indoor units differs per space: 152 for coils and discrete
inputs, 156 for input and holding registers. Getting that wrong reads a
neighbouring unit and looks like plausible data, so it is defined once here.

This module is the counterpart of ``app/devices/toshiba.py`` in the ``modbus-ui``
repository. Both describe the same hardware; ``tests/test_map_parity.py`` fails
when they drift apart.
"""

# Copyright 2026 JI ENGINEERING
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Final

STRIDE_BITS: Final = 152  # coil / discrete
STRIDE_WORDS: Final = 156  # input / holding

# Najdłuższy odczyt rejestrów, który wraca z instalacji. Zmierzone 2026-09-03 na
# interfejsie za bramką Waveshare 9600 8E1: 16 rejestrów wraca zawsze, 17 w 2 z 3
# prób, 20 i więcej nigdy - ani razu w 15 próbach. Próg jest twardy i nie zależy od
# czasu: RTT trzyma się ~730 ms niezależnie od długości odczytu, także z hosta w tym
# samym VLAN-ie, więc to nie jest timeout transmisji. Powyżej progu nie ma wyjątku
# ani błędu, jest cisza, a pojedynczy blok input o długości 38 rejestrów zabierał
# ze sobą model, numer seryjny i wszystkie odczyty jednostki.
MAX_READ_LEN: Final = 16

# Central control address range with "old controller", which RAC interfaces
# require (SM p. 16 and p. 33).
ADDR_MIN: Final = 1
ADDR_MAX: Final = 64

# --------------------------------------------------------------------------- słowniki

HVAC_MODE_READ: Final = {
    0: "invalid", 1: "heat", 2: "cool", 3: "dry",
    4: "fan_only", 5: "auto_heat", 6: "auto_cool", 7: "unfix",
}
HVAC_MODE_WRITE: Final = {"unfix": 0, "heat": 1, "cool": 2, "dry": 3, "fan_only": 4, "auto": 5}

FAN_MODES: Final = {1: "stop", 2: "auto", 3: "high", 4: "medium", 5: "low", 7: "high_plus", 8: "low_plus"}
LOUVER_MODES: Final = {1: "swing", 2: "f1", 3: "f2", 4: "f3", 5: "f4", 6: "f5", 7: "stop"}

# RAC obsługuje tylko swing i stop (OM RAC I/F, uwaga przy żaluzji).
LOUVER_RAC: Final = (1, 7)

SAVE_MODES: Final = {0: "no_limit", 1: "variable", 2: "half", 3: "full_save"}
# "100% Save" jest w tabeli rejestrów, ale manual oznacza je jako niedostępne dla RAC.
SAVE_UNAVAILABLE_RAC: Final = (3,)

RC_LOCK_BITS: Final = ("onoff", "mode", "setpoint", "louver", "fan", "ventilation")
FUNC_BITS: Final = ("pure_filter", "hi_power", "eco", "quiet_fcu", "silence_cdu")

# Check codes of the RAC interface, from Service Manual A10-2103-7 rev. 7, section 9-3.
# The interface reports one word in `30003+156(n-1)`; 0 means no error. Which table
# applies depends on the interface's type setting, so both are kept: the two ranges do
# not overlap (residential codes are 0x40xx, light commercial ones are 0x00-0xFD).
# Value: (code shown on the remote controller, description as in the manual).
CHECK_CODES_RESIDENTIAL: Final = {
    0x4004: ("04", "Serial signal error"),
    0x4007: ("07", "Case thermo error"),
    0x400C: ("0C", "TA sensor (Room temperature sensor) error"),
    0x400D: ("0D", "TC sensor (Heat exchanger temperature sensor) error"),
    0x400E: ("0E", "Refrigerant leak sensor error"),
    0x400F: ("0F", "TCJ sensor (Heat exchanger temperature sensor) error"),
    0x4011: ("11", "Indoor fan motor error"),
    0x4012: ("12", "Indoor P.C. board error"),
    0x4014: ("14", "G-Tr short circuit protection error"),
    0x4016: ("16", "Comp position detection circuit error"),
    0x4017: ("17", "Current sensor error"),
    0x4018: ("18", "TE sensor (Outdoor heat exchanger temperature sensor) or TS (Suction pipe temperature sensor) error"),
    0x4019: ("19", "TD sensor (Discharge pipe temperature sensor) error"),
    0x401A: ("1A", "Outdoor fan motor error"),
    0x401B: ("1B", "TO sensor (Outdoor temperature sensor) error"),
    0x401C: ("1C", "Compressor system or other error"),
    0x401D: ("1D", "Compressor does not rotate"),
    0x401E: ("1E", "TD sensor (Discharge pipe temperature sensor) over limit"),
    0x401F: ("1F", "Compressor break down"),
    0x4021: ("21", "High pressure is detect"),
    0x4025: ("25", "Refrigerant leak detection"),
    0x4026: ("26", "Gas detector sensor error (only bi-flow)"),
    0x4041: ("41", "UART communication error between RAC IF to RAC"),
}
CHECK_CODES_LIGHT_COMMERCIAL: Final = {
    0x2C: ("C12", "Batch alarm of general-purpose equipment control interface"),
    0x44: ("E04", "Communication circuit error between indoor and outdoor"),
    0x4B: ("E11", "Communication error at optional PCB in indoor unit"),
    0x5F: ("E31", "IPDU communication error"),
    0x61: ("F01", "Indoor TCJ sensor error"),
    0x63: ("F03", "Indoor TC1 sensor error"),
    0x64: ("F04", "TD1 sensor error"),
    0x66: ("F06", "TE1/TE2 sensor error"),
    0x68: ("F08", "TO sensor error"),
    0x6A: ("F10", "Indoor TA/TSA sensor error"),
    0x7D: ("F29", "Indoor other error"),
    0x81: ("H01", "Compressor break down"),
    0x82: ("H02", "Magnet switch / Over current operation / Compressor error"),
    0x83: ("H03", "Current detection circuit error"),
    0x84: ("H04", "Comp-1 case thermo operation"),
    0xBD: ("J29", "Refrigerant leak sensor error"),
    0xBE: ("J30", "Refrigerant leak detection"),
    0xBF: ("J31", "Refrigerant leak sensor life"),
    0xE3: ("P03", "Discharge temp. TD1 error"),
    0xEC: ("P12", "Indoor fan motor error"),
    0xF4: ("P20", "High-pressure inverse error"),
    0xF6: ("P22", "Outdoor fan IPDU error"),
    0xFA: ("P26", "G-Tr short circuit protection error"),
    0xFD: ("P29", "Comp position detection circuit error"),
}
NO_ERROR: Final = "No active error"


def check_code_info(code: int) -> tuple[str, str] | None:
    """(remote controller code, description) for a code word, None if the manual lacks it.

    Releases up to 0.5.0 keyed a small table by the low byte of the residential codes
    (0x04, 0x07 ...), which can never match a real 0x40xx word; the low byte is still
    accepted when the high byte is empty, so a firmware that reports it that way works too.
    """
    if code in CHECK_CODES_RESIDENTIAL:
        return CHECK_CODES_RESIDENTIAL[code]
    if code in CHECK_CODES_LIGHT_COMMERCIAL:
        return CHECK_CODES_LIGHT_COMMERCIAL[code]
    return CHECK_CODES_RESIDENTIAL.get(0x4000 | code) if code <= 0xFF else None


def check_code_text(code: int) -> str:
    """One line for a check code: "19: TD sensor ... error", or the raw word when unknown."""
    if code == 0:
        return NO_ERROR
    info = check_code_info(code)
    return f"{info[0]}: {info[1]}" if info else f"0x{code:04X}"


# --------------------------------------------------------------------------- offsety

# Nazwa -> offset względem bazy jednostki. Bazy: bits = 152*(n-1), words = 156*(n-1).
COIL: Final = {
    "onoff": 0, "filter_reset": 1,
    "hi_power": 57, "eco": 58, "quiet": 59, "silence": 60,
}
# "thermo" (10004) stays in the map for the emulator and the panel, but a RAC interface
# never sets it: service manual rev. 7, 7-4 leaves thermo status off the RAC list.
DISCRETE: Final = {
    "onoff": 0, "filter_sign": 1, "alarm": 2, "thermo": 3,
    "st_pure_filter": 80, "st_hi_power": 81, "st_eco": 82, "st_quiet": 83, "st_silence": 84,
}
INPUT: Final = {
    "room_temp": 0, "setpoint": 1, "check_code": 2,
    "model": 6, "serial": 14, "capacity": 22,
    "mode": 35, "fan": 36, "louver": 37, "func_status": 58,
}
HOLDING: Final = {
    "setpoint": 0, "hours": 1, "mode": 6, "fan": 7, "louver": 8,
    "rc_lock": 9, "save": 10,
}

# Zapis trafia do rejestru polecenia, a stan jednostki czyta się z innego - tego,
# który interfejs odświeża po obejściu magistrali Uh. Ta mapa mówi, gdzie pokazać
# zapisaną wartość, zanim interfejs ją potwierdzi. Pola spoza mapy (rc_lock, save)
# czyta się z tego samego rejestru, do którego się pisze.
WRITE_STATUS: Final = {
    ("holding", "setpoint"): ("input", "setpoint"),
    ("holding", "mode"): ("input", "mode"),
    ("holding", "fan"): ("input", "fan"),
    ("holding", "louver"): ("input", "louver"),
    ("coil", "onoff"): ("discrete", "onoff"),
    ("coil", "hi_power"): ("discrete", "st_hi_power"),
    ("coil", "eco"): ("discrete", "st_eco"),
    ("coil", "quiet"): ("discrete", "st_quiet"),
    ("coil", "silence"): ("discrete", "st_silence"),
}

# Rejestry wielosłowowe (ASCII).
WIDTH: Final = {("input", "model"): 8, ("input", "serial"): 8}

TEMP_MIN: Final = 17.0
TEMP_MAX: Final = 30.0
TEMP_STEP: Final = 0.5


def base(space: str, unit: int) -> int:
    """Adres bazowy jednostki w danej przestrzeni."""
    stride = STRIDE_BITS if space in ("coil", "discrete") else STRIDE_WORDS
    return stride * (unit - 1)


def addr(space: str, unit: int, key: str) -> int:
    """Adres na drucie dla jednego pola jednej jednostki."""
    table = {"coil": COIL, "discrete": DISCRETE, "input": INPUT, "holding": HOLDING}[space]
    return base(space, unit) + table[key]


def locate(space: str, address: int) -> tuple[int, str] | None:
    """Odwrotność addr(): adres na drucie -> (jednostka, pole)."""
    table = {"coil": COIL, "discrete": DISCRETE, "input": INPUT, "holding": HOLDING}[space]
    stride = STRIDE_BITS if space in ("coil", "discrete") else STRIDE_WORDS
    unit, offset = divmod(address, stride)
    for key, off in table.items():
        if off == offset:
            return unit + 1, key
    return None


def width(space: str, key: str) -> int:
    return WIDTH.get((space, key), 1)


def blocks_for_unit(space: str, unit: int, max_len: int = MAX_READ_LEN, max_gap: int = 12) -> list[tuple[int, int]]:
    """Scala pola jednej przestrzeni w ciągłe zakresy odczytu.

    Bez tego wychodzi jedna transakcja na pole. Przy 9600 bps to jest różnica
    między 27 a 96 ramkami na cykl odpytania trzech jednostek.
    """
    table = {"coil": COIL, "discrete": DISCRETE, "input": INPUT, "holding": HOLDING}[space]
    spans = sorted(
        (base(space, unit) + off, base(space, unit) + off + width(space, key) - 1)
        for key, off in table.items()
    )
    out: list[tuple[int, int]] = []
    lo, hi = spans[0]
    for a, b in spans[1:]:
        if a - hi - 1 <= max_gap and (b - lo + 1) <= max_len:
            hi = max(hi, b)
        else:
            out.append((lo, hi - lo + 1))
            lo, hi = a, b
    out.append((lo, hi - lo + 1))
    return out


def decode_ascii(words: list[int]) -> str:
    """Rejestry tekstowe. Same zera = jednostki nie ma na magistrali.

    Manual nie zwraca wyjątku 0x07 dla nieobecnej jednostki - oddaje poprawną
    ramkę wypełnioną zerami. Nazwa modelu jest jedynym pewnym testem obecności.

    Same 0xFF znaczą "pole nieobsługiwane": tak odpowiada numer seryjny na każdym
    z trzech RAC I/F (zmierzone 2026-09-28). Dekodowane przez "replace" dawały
    16 znaków U+FFFD, czyli niepusty tekst - więc bajty spoza drukowalnego ASCII
    są odrzucane, a nie zastępowane.
    """
    raw = b"".join(int(w).to_bytes(2, "big") for w in words)
    return "".join(chr(b) for b in raw if 0x20 <= b <= 0x7E).strip()


# Dane samego interfejsu, na slave N (za blokiem jednostki 64). Service manual rev. 7,
# tabela input: 39985-39992 nazwa oprogramowania w ASCII i w ostatnim słowie wersja
# razy 100, 39993 stan interfejsu. Jedna ramka, 9 słów - poniżej limitu 16 bramki.
IFACE_INFO_START: Final = 39985 - 30001
IFACE_INFO_COUNT: Final = 9
IFACE_STATUS: Final = {
    0: "undetermined", 1: "initializing", 2: "operating", 3: "operating_with_controller",
    5: "suspended", 6: "address_duplicated",
}


def decode_iface_info(words: list[int]) -> tuple[str | None, str | None, str | None]:
    """(nazwa oprogramowania, wersja "x.yy", stan) z bloku 39985-39993.

    Na zainstalowanym interfejsie: "BMS-IFMB1280U", słowo 0x0193 = 4.03, stan 2
    (zmierzone 2026-09-28). Wersja siedzi w ostatnim słowie pola tekstowego, więc
    tekst dekodowany jest bez niego - inaczej 0x01 0x93 doklejałoby się do nazwy.
    """
    if len(words) < IFACE_INFO_COUNT:
        return None, None, None
    name = decode_ascii(words[:7]) or None
    raw = words[7]
    version = None if raw in (0, NOT_AVAILABLE) else f"{raw // 100}.{raw % 100:02d}"
    status = IFACE_STATUS.get(words[8])
    return name, version, status


# Tekst, który RAC I/F oddaje zamiast nazwy modelu, gdy jej nie zna. Zmierzone
# 2026-09-28: jednostka 1 zwraca "RAS-B10N4KVRG-E1", jednostki 2 i 3 dokładnie to.
# Obecność potwierdza (adapter odpowiada), ale modelem nie jest.
PLACEHOLDER_MODELS: Final = frozenset({"RACIF Model Name"})

# "Brak wartości" w rejestrze słowa. 0xFFFF przychodzi z instalacji jako moc
# (30023) na wszystkich jednostkach; 0x8000 i 0x7FFF to skrajne wartości int16,
# których żaden czujnik temperatury nie poda.
NOT_AVAILABLE: Final = 0xFFFF
TEMP_SENTINELS: Final = frozenset({0xFFFF, 0x8000, 0x7FFF})


def signed(word: int) -> int:
    return word - 0x10000 if word >= 0x8000 else word


def word_or_none(word: int | None) -> int | None:
    """Słowo bez znaku, z 0xFFFF zamienionym na brak wartości."""
    return None if word is None or word == NOT_AVAILABLE else word


def tenths(word: int | None) -> float | None:
    """Temperatura albo moc w dziesiątych częściach, ze znakiem.

    Bez odsiewu 0xFFFF wychodzi -0.1 (signed), a 0x8000 -3276.8 - obie wartości
    wyglądają w HA na prawdziwy pomiar.
    """
    if word is None or word in TEMP_SENTINELS:
        return None
    return signed(word) / 10
