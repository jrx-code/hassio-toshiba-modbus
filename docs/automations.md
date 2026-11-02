# Automations and dashboards

The examples use generic entity ids; replace them with yours (*Settings, Devices & services, Entities*).
Entity ids follow the language of the Home Assistant instance, so `sensor.outdoor_unit_power_draw` becomes
`sensor.agregat_pobor_mocy` on a Polish one.

## Turn heating off when a window is open

The integration controls what a unit does but does not supervise it. This switches a unit off when
its window has been open for two minutes and the unit is heating:

```yaml
alias: Bedroom split off when the window is open
triggers:
  - trigger: state
    entity_id: binary_sensor.bedroom_window
    to: "on"
    for: "00:02:00"
conditions:
  - condition: state
    entity_id: climate.bedroom
    state: heat
actions:
  - action: climate.turn_off
    target:
      entity_id: climate.bedroom
mode: single
```

A unit started by hand (remote control or Home Assistant) stays under your control; the
automation only ends what you started. A supervised manual start also needs a grace period for the
"nobody here" rule, because a presence sensor can lag behind the person who just picked up the remote.

## Tell me when a unit reports an error

```yaml
alias: Split alarm
triggers:
  - trigger: state
    entity_id: binary_sensor.bedroom_alarm
    to: "on"
actions:
  - action: notify.notify
    data:
      title: "Air conditioner alarm"
      message: >-
        {{ state_attr('climate.bedroom', 'check_code_description') }}
```

The text reads like `19: TD sensor (Discharge pipe temperature sensor) error`. Faults of the outdoor unit
arrive the same way, because the interface reports them as the indoor unit's check code.

## Is the outdoor unit working?

With a power meter chosen in the setup, the *Running* sensor of the **Outdoor unit** device answers it. For
example, a reminder when the system has run for more than twelve hours without a break:

```yaml
alias: Outdoor unit has been running for 12 hours
triggers:
  - trigger: state
    entity_id: binary_sensor.outdoor_unit_running
    to: "on"
    for: "12:00:00"
actions:
  - action: notify.notify
    data:
      message: "The outdoor unit has been running for twelve hours."
```

## Energy per day, month and year

If the energy sensor you picked only ever goes up (a meter that reports a lifetime total), use it as it is and add
three *Utility meter* helpers on it (cycle `daily`, `monthly`, `yearly`).

If the meter reports energy of the **last hour**, which falls as the window moves, do not use it for statistics.
Integrate the power instead:

1. *Settings, Devices & services, Helpers, Create helper, Integral.* Input sensor: the power sensor. Method `left`
   (the power sensor reports changes, so the previous value holds until the next one), metric prefix `k`, time unit `h`,
   and a *Max sub-interval* of 30 seconds so that a flat reading keeps adding up.
2. *Create helper, Utility meter* three times, with the new energy sensor as the source and the cycle `daily`,
   `monthly` and `yearly`.
3. The Integral sensor can also be added to the *Energy* dashboard as an individual device.

On a test site, 75 seconds of integration added 5.0 Wh against 5.64 Wh computed from the average power, which is within
the one-watt-hour resolution of three decimals. While Home Assistant is down the integral does not count; at a few
kilowatts a three-minute restart loses a fraction of a kilowatt-hour. The first cycle of each utility meter is incomplete.
See the Home Assistant documentation of the
[Integral](https://www.home-assistant.io/integrations/integration/) and
[Utility meter](https://www.home-assistant.io/integrations/utility_meter/) integrations.

## A dashboard card

A thermostat card for a unit, with the power limit and the special functions underneath:

```yaml
type: vertical-stack
cards:
  - type: thermostat
    entity: climate.bedroom
  - type: entities
    entities:
      - entity: select.bedroom_power_limit
      - entity: switch.bedroom_eco
      - entity: switch.bedroom_hi_power
      - entity: switch.bedroom_quiet_fcu
      - entity: switch.bedroom_silence_cdu
```
