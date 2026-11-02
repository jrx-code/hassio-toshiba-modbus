# Troubleshooting

Start with *Download diagnostics* on the interface device and with the **Communication errors**, **Messages without
response** and **Interface status** sensors: they separate "the network is broken" from "the bus is noisy" from
"the interface refuses".

## Setup errors

| Message | Cause | What to check |
|---|---|---|
| Nothing is listening on that address and port | The TCP connection is refused or times out | Gateway address and port. Serial gateways usually listen on 8899 or 502, the emulator on 5502 |
| The connection is up but the interface does not answer | The socket is open, no valid reply came | Framing (`rtuovertcp` or `tcp`), the slave address against switch **SW1**, and that nothing else is polling the bus at the same moment |
| This gateway is already in use with a different framing or port | The core `modbus` integration shares one connection per gateway and already holds it with other settings | Use the same settings as the existing entry |
| This interface is already configured | Same host and slave address | Open the existing entry |

## Entities

| Symptom | Cause and fix |
|---|---|
| All entities of a unit are `unavailable` | The unit does not answer. A missing unit returns a valid frame of zeros, so presence is judged by the model-name string; check the RAC adapter and the Uh line |
| An address you cleared comes back, or one you want is missing | Cleared addresses are remembered as excluded. Restore them under *Configure* on the entry |
| A new adapter does not appear | Press *Find indoor units* on the interface device, or wait for the background scan (default 300 s) |
| Values update slowly | The bus costs about 0.8 s per transaction regardless of size: three units take about 24 s of a 30 s interval. Fewer frames is the only lever; a faster serial line buys nothing |
| A written value jumps back for a moment | The interface needs a poll cycle before the status registers change. The written value is shown at once and confirmed by the poll, or dropped after 60 s if the unit contradicts it |
| `Check code` shows `0x....` | The code is not in the manual's table. Open an issue with the value and the unit model |
| No `hvac_action`, no compressor sensor | By design, see [Entities](entities.md#why-there-is-no-hvac_action) |
| No *Outdoor unit* device | Choose a power sensor under *Configure* on the entry, step *Outdoor unit* |
| *Running* is `unknown` | The chosen power sensor is `unavailable` or not a number |

## The bus

| Symptom | Cause |
|---|---|
| **Communication errors** rise while the connection looks fine | Interference on RS-485, or a second master on the same line |
| Replies look like they answer another request | A second client on the gateway. Gateways accept several TCP clients but do not correlate replies to them; a master outside Home Assistant is still a second master |
| Reads of more than 16 registers never answer | The bus answers up to 16 registers per read (17 about two times in three, 20 and more never). The integration already caps every read; this matters for scripts you write yourself |
| The interface works for a few units and nothing for the rest | `Central controller ID` is on the factory `ID20` instead of `old controller`; the site is also capped at 64 indoor units |
| Interface status `suspended` or `address_duplicated` | A configuration fault on the interface: it answers diagnostics but no longer serves the units |

## Logs

```yaml
logger:
  default: warning
  logs:
    custom_components.toshiba_modbus: debug
```

Occasional `no answer within 3 s` lines in the log are the bus dropping a single frame; the next cycle recovers.
A line on every cycle means one of the causes above.

## Testing without hardware

`tools/emulator.py` answers like the real interface; see [Contributing](../CONTRIBUTING.md#testing-without-hardware).
It is the quickest way to tell a problem in your network from a problem in the integration.
