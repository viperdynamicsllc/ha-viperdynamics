# Viper Dynamics for Home Assistant

Discover and control Viper Dynamics smart displays from Home Assistant over your local network.

| Device | Controls |
|---|---|
| Stargate P1S | Gate open/close, mode, dismiss alarm |
| Stargate P3M | Mode, brightness, automatic brightness, alarm volume, test alarm, firmware updates |
| Stargate P4X | Mode, brightness, automatic brightness, screen tilt, alarm volume, test alarm, firmware updates |
| Nether Portal | Mode, brightness, clock animation, player |
| Nether Portal 7 Pro | Mode, brightness, volume, alarm volume, sound, clock animation, firmware updates |
| WoW Dark Portal | Mode, brightness, mascot, character |

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
