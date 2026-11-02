# Hardware notes

What cost time to find. Page references are to the Service Manual of the Modbus interface, A10-2103-7 rev. 7.

## The interface

- **It occupies three slave addresses.** `N` covers central addresses 1 to 64, `N+1` covers 65 to 128, `N+2` answers loopback
  but returns exception `0x02` for register reads.
- **`Central controller ID` must be `old controller`** when RAC adapters are used (p. 16). The factory value is ID20 and it
  silently does not work. That also caps the site at 64 indoor units.
- **A missing indoor unit does not raise an exception.** It returns a valid frame of zeros, so zero cannot distinguish "off"
  from "not there". The model-name string is the only reliable presence test.
- **The address stride differs per space:** 152 for coils and discrete inputs, 156 for input and holding registers.
- **A read longer than 16 registers comes back as silence,** with no exception and no error, which reads exactly like a dead bus.
- **One master per bus.** See [Troubleshooting](troubleshooting.md#the-bus).
- **The interface reports its own software version** in registers `39985` to `39992` (ASCII, with the version times 100 in the
  last word) and its status in `39993`.

## The RAC adapter

- The serial-number register answers `0xFF` only. The serial comes from the nameplate or the Toshiba app.
- Some adapters answer the model register with the placeholder `RACIF Model Name`.
- **The thermo bit (`10004`) is never set,** so a RAC interface cannot say whether the unit is cooling (section 7-4 leaves
  "Thermo status" off the RAC function lists). Measured on the installed units through a whole day of cooling.

## What Modbus cannot give you

The RAC function list (section 7-4, "Residential AC type") covers power, setpoint, mode, fan, louver, save operation rate,
the special functions, alarm, room temperature, check code, model and the temperature ranges. It does **not** include:

| Not available over Modbus | Where it comes from instead |
|---|---|
| Outdoor unit data: compressor load, refrigerant and pipe temperatures, outdoor temperature | Nowhere in the RAC interface. Section 8-2 "Outdoor unit" is EER and VRF capacity data addressed by outdoor line, not RAC; `N+2` answers `0x02`. A third-party ESP32 controller on the same UART is reported to expose more, but it excludes the Modbus interface |
| Energy consumption of the system | A power meter on the outdoor unit's supply, see [Configuration](configuration.md#step-4-outdoor-unit-optional) |
| Outdoor temperature | Any outdoor sensor you already have in Home Assistant |
| 8 °C heating mode, fireplace mode, self-cleaning, seven fan speeds, ten louver positions | Only the Toshiba cloud, as exposed by the `toshiba_ac_community` integration; the Modbus map has five fan speeds and swing or stop |
| Firmware versions of the units | Only the Toshiba cloud |

**Faults of the outdoor unit do reach you:** the interface reports them as the indoor unit's check code (`1F: Compressor break
down`, `19: TD sensor error` and so on), which the integration decodes.

## Multisplit systems

A multisplit has one outdoor unit for several indoor ones. Anything measured on the outdoor unit belongs to the whole
system and to none of the indoor units. A power meter says that the system works, not which room asked for it.
