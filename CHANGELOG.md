# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/) from 1.0.0 on.

## [1.0.0] - 2026-11-02

First stable release. The integration has run against real hardware (three indoor units, one
outdoor unit, a production Home Assistant) since September; 1.0.0 marks the configuration,
the entity set and the attribute names below as the public interface.

### Added
- **Check codes are decoded.** The tables of Service Manual A10-2103-7 rev. 7, section 9-3, for
  both interface types (residential `0x40xx`, light commercial `0x00`-`0xFD`). The check-code
  sensor and the climate attribute now read `19: TD sensor (Discharge pipe temperature sensor)
  error` instead of a raw number; a code missing from the manual is shown as `0xNNNN`.
- English attribute names on the climate entity: `check_code`, `check_code_description`,
  `rac_functions`.
- A pytest job in CI (including the transport tests and the register-map parity check against the
  `modbus-ui` panel), contributed by grok-bot.
- Documentation: installation, configuration, entity reference, automation examples,
  troubleshooting, hardware notes, and diagrams of the architecture, the setup flow and the
  device model. Screenshots refreshed from Home Assistant 2026.9.

### Changed
- The check-code sensor states `No active error` instead of `brak błędu`.
- Device names are translated instead of hard-coded in Polish: `Modbus interface (host)` and `Outdoor unit` (`Interfejs Modbus (host)` and `Agregat` on a Polish
  instance). Entity ids of existing installs do not change; new installs get entity ids from the English names.

### Deprecated
- The Polish attributes `kod_bledu`, `kod_bledu_opis` and `funkcje_rac` still carry the same
  values as their English replacements, so dashboards written against 0.x keep working. They will
  be removed in 2.0.0.

### Fixed
- The check-code table keyed by the low byte (`0x04`, `0x07` ...) could never match the
  `0x40xx` words a residential interface reports. The low byte is still accepted when the high
  byte is empty.

## [0.5.0] - 2026-11-02

### Added
- **Outdoor unit device ("Agregat")** fed by an external power meter on the outdoor unit's supply (a
  DIN relay with a meter, a smart plug): power, energy and a `Running` binary sensor. One meter for
  the whole system, because a multisplit has one outdoor unit for several indoor ones; there is no
  `hvac_action` per indoor unit for the same reason.
- The setup flow offers the optional serial-number and outdoor-unit steps (until now they existed
  only in the options). An empty bus (no indoor units yet) still offers the outdoor-unit step.

## [0.4.5] - 2026-10-20
### Changed
- Repository renamed to `hassio-toshiba-modbus`; safety notes added to the documentation.
  Accepted into the default HACS store.

## [0.4.4] - 2026-09-29
### Changed
- Logos trimmed to the `home-assistant/brands` specification; CI validates with the HACS action and
  hassfest.

## [0.4.3] - 2026-09-28
### Added
- A model per unit in the options, for adapters that answer the model register with a placeholder.

## [0.4.2] - 2026-09-28
### Added
- Interface status, interface software version and four rare-event counters (read every five
  minutes); serial numbers can be typed in the options.

## [0.4.1] - 2026-09-28
### Removed
- `hvac_action` and the "Compressor" sensor: a RAC interface never sets the thermo bit, so both
  showed `idle` while the unit cooled.

## [0.4.0] - 2026-09-28
### Changed
- The Modbus link is borrowed from the core `modbus` integration (Home Assistant 2026.9), which
  shares one connection per gateway and queues requests, instead of the integration opening its own.

## [0.3.2] - 2026-09-28
### Fixed
- Values the real hardware reports; writes show immediately and are confirmed by the next poll.
### Added
- `tools/scan_bus.py`, a bus scan that says which layer is silent.

## [0.3.1] - 2026-09-03
### Fixed
- A read is capped at 16 registers, which is all the bus answers (longer reads come back as silence).

## [0.3.0] - 2026-09-03
### Changed
- Licence: Apache-2.0 with a `NOTICE`, instead of MIT.

## [0.2.1] - 2026-09-03
### Fixed
- The unit picker was half Polish in an English dialog.

## [0.2.0] - 2026-09-03
### Added
- First public version: climate, select, switch, button, sensor and binary sensor per indoor
  unit; interface device with bus diagnostics; one setup dialog to pick and name units; an
  interface with no indoor units is a valid entry; Toshiba artwork and entity icons; release zip.

[1.0.0]: https://github.com/jrx-code/hassio-toshiba-modbus/releases/tag/v1.0.0
[0.5.0]: https://github.com/jrx-code/hassio-toshiba-modbus/releases/tag/v0.5.0
[0.4.5]: https://github.com/jrx-code/hassio-toshiba-modbus/releases/tag/v0.4.5
