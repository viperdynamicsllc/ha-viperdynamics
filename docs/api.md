# Viper HA API v1

Every Viper Dynamics device firmware exposes this small JSON API on port 80 so the
Home Assistant integration can discover, identify, read and control it. The existing
web UI routes are untouched; these endpoints call the same internal functions.

There is no authentication — the API is LAN-only, like the existing web UI.

## mDNS

Advertise `_viperdyn._tcp` on port 80 (in addition to the existing `_http._tcp`).
The instance name is the device hostname (e.g. `P4X-1A2`).

| TXT key | Example | Meaning |
|---|---|---|
| `id` | `a1b2c3d4e5f6` | Full Wi-Fi STA MAC, lowercase hex, no separators. Stable unique ID. |
| `model` | `stargate_p4x` | Model slug (see below). |
| `fw` | `2.0.58` | Firmware version. |
| `api` | `1` | API version. |

Model slugs: `stargate_p1s`, `stargate_p3m`, `stargate_p4x`, `nether_portal`,
`nether_portal_7_pro`, `dark_portal`.

## `GET /api/info`

```json
{
  "manufacturer": "Viper Dynamics",
  "model": "stargate_p4x",
  "model_name": "Stargate P4X",
  "id": "a1b2c3d4e5f6",
  "name": "P4X-1A2",
  "mac": "9c:13:9e:d6:db:28",
  "fw": "2.0.58",
  "api": 1,
  "capabilities": ["mode", "brightness", "backlight_auto", "alarm_volume", "rotation",
                   "alarm_test", "restart", "ota"],
  "modes": ["Clock", "Continuous Stargate", "Photo Frame"],
  "brightness_min": 0,
  "rotation_min": -10,
  "rotation_max": 10
}
```

`id` is derived from the chip's factory MAC and never changes. `mac` is the Wi-Fi MAC the
router sees, which differs from `id` on ESP32-P4 boards (Wi-Fi runs on a companion chip).

Optional option lists, present only with the matching capability:
`clock_anims` (array of strings), `mascots` (array of strings).

## `GET /api/state`

Returns only keys for the device's capabilities.

| Key | Capability | Type | Notes |
|---|---|---|---|
| `mode` | `mode` | int | Index into `info.modes`. |
| `brightness` | `brightness` | int 0–100 | Current manual brightness; `0` while the backlight is off. |
| `backlight_auto` | `backlight_auto` | bool | Automatic (sunrise/sunset) backlight. |
| `volume` | `volume` | int 0–100 | Media/sound volume. |
| `alarm_volume` | `alarm_volume` | int 0–100 | |
| `sound` | `sound` | bool | Sound effects enabled. |
| `rotation` | `rotation` | int | Screen tilt, `rotation_min`..`rotation_max`. |
| `gate` | `gate` | object | `{"open": bool, "busy": bool}` |
| `clock_anim` | `clock_anim` | string | One of `info.clock_anims`. |
| `mascot` | `mascot` | string | One of `info.mascots`. |
| `player` | `player` | object | Game character info; free-form string/number fields. `name` is the headline value. |
| `alarm_active` | `alarm_ack` | bool | An alarm is ringing and can be dismissed. |
| `update` | `ota` | object | `{"installed": str, "latest": str\|null, "notes": str, "in_progress": bool, "percent": int, "can_install": bool}`. `can_install` defaults to true; send false when the device can only be updated from its own web page. |

## `POST /api/control`

Body: JSON object with any subset of the writable keys. Applies them in order and returns
the new state (same shape as `/api/state`). Unknown keys are ignored. Errors return
`400 {"error": "..."}`. Body limit: 1 KiB.

Devices with `ota` start a manifest check when `/api/state` is polled (at most every 6 h),
so `update.latest` fills in shortly after Home Assistant connects.

| Key | Value |
|---|---|
| `mode` | int |
| `brightness` | int 0–100. `0` turns the backlight fully off (see below). Other values set the manual level, raised to the panel's lowest usable level if needed, and turn `backlight_auto` off unless the same request sets it. |
| `backlight_auto` | bool |
| `volume`, `alarm_volume` | int 0–100 |
| `sound` | bool |
| `rotation` | int |
| `gate` | `"open"` \| `"close"` \| `"toggle"` |
| `clock_anim`, `mascot` | string |
| `action` | `"alarm_test"` \| `"alarm_ack"` \| `"restart"` \| `"install_update"` (each needs the same-named capability; `install_update` needs `ota`) |

### Backlight off (required for every device with `brightness`)

Every device with a backlight must let Home Assistant turn it fully off, and report
`brightness_min: 0` so the Home Assistant slider reaches 0.

- `brightness: 0` turns the backlight off without changing the saved level or `backlight_auto`.
- Any `brightness` > 0, `backlight_auto: true`, or a brightness/auto change from the device's
  web UI turns it back on.
- A touch on the screen wakes it; that touch is not passed to the UI.
- A ringing alarm lights the screen while it rings, then it goes dark again.
- The off state is not saved, so the screen is always on after a power cycle.

Example:

```sh
curl -X POST -H 'Content-Type: application/json' -d '{"mode":2}' http://P4X-1A2.local/api/control
```
