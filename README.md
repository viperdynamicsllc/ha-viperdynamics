# Viper Dynamics for Home Assistant

Discover and control Viper Dynamics smart displays from Home Assistant over your local network.

| Device | Firmware with HA support | Controls |
|---|---|---|
| Stargate P1S | 1.1.0 | Gate open/close, mode, brightness / screen off, dismiss alarm, restart |
| Stargate P3M | 7.0.3 | Mode, brightness / screen off, auto-brightness, alarm volume, test/dismiss alarm, restart, firmware updates |
| Stargate P4X | 2.0.61 | Mode, brightness / screen off, auto-brightness, screen tilt, alarm volume, test/dismiss alarm, restart, firmware updates |
| Nether Portal | 1.2.0 | Mode, brightness / screen off, auto-dim, player stats, restart |
| Nether Portal 7 Pro | 2.1.31 | Mode, brightness / screen off, auto-dim, volume, alarm volume, sound, test/dismiss alarm, restart, firmware update notices |
| WoW Dark Portal | v8+ | Mode, brightness / screen off, auto-dim, mascot, character sheet, restart |

Setting brightness to 0 turns the screen fully off; touching the screen (on touch models) or raising the brightness turns it back on.

The integration builds entities from what each device reports, so features can vary with firmware version.

## Requirements

- Device firmware with Home Assistant support (Viper HA API v1, see [docs/api.md](docs/api.md)). Update your device to the latest firmware.
- The device and Home Assistant on the same network, with mDNS allowed between them.

## Installation (HACS)

1. In HACS, open the menu → **Custom repositories**.
2. Add `https://github.com/viperdynamicsllc/ha-viperdynamics` with type **Integration**.
3. Install **Viper Dynamics** and restart Home Assistant.

## Setup

Powered-on devices appear under **Settings → Devices & services → Discovered**. Click **Add** and confirm.

To add a device by hand, choose **Add integration → Viper Dynamics** and enter its IP address or hostname (for example `P4X-1A2.local`).

## Development

```sh
pip install -r requirements_test.txt
pytest
```
