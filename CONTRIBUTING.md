# Contributing

Thanks for looking. Bug reports with a [diagnostics download](docs/entities.md#diagnostics) and the unit model are
the most useful contribution; a check code that shows up as `0x....` is a bug report worth filing.

## Layout

| | |
|---|---|
| `custom_components/toshiba_modbus/` | The integration. `registers.py` is the register map and the check-code tables, with no Home Assistant imports; `power.py` is the pure part of the outdoor-unit meter |
| `tests/` | Pytest. Pure modules are loaded by path, so most tests need no Home Assistant |
| `tools/emulator.py` | A dependency-free Modbus RTU-over-TCP server that answers like the real interface |
| `tools/scan_bus.py` | A bus scan that says which layer is silent |
| `tools/build_release.sh` | Builds the release archives from a clean checkout of `HEAD` |
| `docs/` | The documentation; diagrams are hand-written SVG in `docs/images/` |

## Tests

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pytest "modbus-connection==4.12.3"
git clone --depth 1 https://github.com/jrx-code/modbus-ui.git ../modbus-ui     # for the map-parity test
MODBUS_UI_APP=../modbus-ui/app pytest tests/ -q
```

`tests/test_map_parity.py` compares the register map with the `modbus-ui` panel's copy, which describes the same
hardware. The copy is duplicated on purpose (the panel is dependency-free and public) and the test fails when the
addresses drift apart. Fix the map, never the test. Without the checkout the test skips itself.

CI runs the same pytest job plus the HACS action and hassfest.

## Testing without hardware

```bash
python3 tools/emulator.py --port 5502 --units 1,2,3 --absent 3
```

Then add the integration against `<host>:5502` with framing `rtuovertcp`. Unit 3 is absent by default, so there is
something to check `unavailable` against. `--no-serial 1,2,3` makes the units answer the serial register with `0xFF`,
and `--placeholder-model 2,3` makes them answer `RACIF Model Name`, like the real adapters.

## Changing the code

- Every source file carries `SPDX-License-Identifier: Apache-2.0`.
- A new entity needs its name in `strings.json`, `translations/en.json` and `translations/pl.json`, and an entry in
  `icons.json`. Icon names are validated against the running instance; an unknown name renders as blank space, not an error.
- A new option goes through the shared field builders in `config_flow.py`, so that the setup flow and the options flow cannot drift apart.
- The options flow replaces the options wholesale, so every step has to carry the values it does not edit.
- Do not open a private Modbus client next to the one borrowed from the core: gateways deliver replies to the wrong client.
- Read the "Gotchas" in [`CLAUDE.md`](CLAUDE.md) before touching the transport, the coordinator or the config flow; each one cost a measurement on real hardware.
- Test on a spare Home Assistant instance, not on the one that heats your house.

## Releasing

1. Update `CHANGELOG.md` and the version in `custom_components/toshiba_modbus/manifest.json`.
2. `tools/build_release.sh` writes `dist/`: `toshiba_modbus.zip` (what HACS downloads, files at the archive root), the
   versioned zip and tarball, and `SHA256SUMS.txt`.
3. Tag `vX.Y.Z` on `main` and create the GitHub release with those four files attached. HACS needs the
   `toshiba_modbus.zip` asset (`hacs.json` sets `zip_release`).
4. Check that the Validate workflow for the release commit has finished green.

Versions follow [Semantic Versioning](https://semver.org/) from 1.0.0 on. Entity ids, attribute names and the options
are the public interface; deprecations stay for a full major version and are listed under *Deprecated* in the changelog.
