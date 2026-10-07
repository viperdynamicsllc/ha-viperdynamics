"""Home Assistant chapter for Viper Dynamics user manuals, plus a quick-start pointer to it.

Shared by every product's gen_docs.py (copy this file next to it). The
generator passes its own helpers and colours, so the pages match each
product's look:

    from ha_docs import manual_section, quickstart_pointer
    manual_section("9", h1, h2, p, bl, story, callout, ST, HA_INFO)
    quickstart_pointer(c, globals(), qx - 14, PH - 87)   # under the QR header text

HA_INFO describes the product:

    HA_INFO = {
        "name": "Stargate P4X",
        "ha_name": "Stargate P4X",          # optional: name Home Assistant shows, if different
        "host": "P4X-XXX",                  # hostname pattern from the boot splash
        "min_fw": "2.0.61",                 # first firmware with Home Assistant support
        "controls": ["Mode: ...", ...],     # what shows up in Home Assistant
        "wake": "touch" | "brightness",     # how a screen turned off from HA comes back
        "firmware": "install" | "notice" | "usb",
        "manual": "StargateP4X-UserManual.pdf",
    }
"""
from __future__ import annotations

REPO_URL = "https://github.com/viperdynamicsllc/ha-viperdynamics"
REPO_SHORT = "github.com/viperdynamicsllc/ha-viperdynamics"
HACS_URL = "hacs.xyz"
HA_MIN = "2025.2"


def _wake_text(info):
    if info.get("wake") == "touch":
        return "Tap the screen, or raise the brightness in Home Assistant, to turn it back on."
    return "Raise the brightness in Home Assistant (or on the web console) to turn it back on."


def _firmware_text(info):
    kind = info.get("firmware")
    if kind == "install":
        return ("New firmware shows up as an update for the device's <b>Firmware</b> entity, "
                "next to your other updates under <b>Settings → Updates</b>. Click <b>Install</b> "
                "and the device updates itself and restarts. Settings and photos stay.")
    if kind == "notice":
        return ("New firmware shows up as an update for the device's <b>Firmware</b> entity under "
                "<b>Settings → Updates</b>, with release notes. Install it from the device's own "
                "Firmware Update page (see the firmware section of this manual).")
    return ("Firmware updates for this model are installed over USB. Home Assistant shows the "
            "installed version on the device page.")


# ── manual ────────────────────────────────────────────────────────────────────

def manual_section(num, h1, h2, p, bl, story, callout, ST, info):
    """Append the Home Assistant chapter to a manual story."""
    from reportlab.platypus import Spacer

    def code(s):
        return "<font face='Courier-Bold' size='9'>%s</font>" % s

    name = info["name"]
    h1(num, "Home Assistant")
    p(f"Your {name} works with <b>Home Assistant</b>, the free smart-home platform. Home Assistant "
      "finds it on your Wi-Fi by itself, and lets you control it from the Home Assistant app, "
      "dashboards and automations. Everything stays on your local network; there is no cloud "
      "account.")

    h2(f"{num}.1  What you need")
    bl(f"Home Assistant {HA_MIN} or newer, on the same network as the {name}.")
    bl(f"<b>HACS</b> (the Home Assistant Community Store) installed in Home Assistant. "
       f"Setup instructions: {code(HACS_URL)}.")
    bl(f"{name} firmware <b>{info['min_fw']}</b> or newer. The version is shown on the boot splash "
       "and on the web console's Firmware Update page.")
    bl(f"The {name} already set up on your home Wi-Fi (see First-Time Setup).")

    h2(f"{num}.2  Install the Viper Dynamics integration")
    p("This is done once per Home Assistant, no matter how many Viper Dynamics devices you have.")
    bl("In Home Assistant, open <b>HACS</b>.")
    bl("Open the <b>three-dot menu</b> (top right) and choose <b>Custom repositories</b>.")
    bl(f"Paste {code(REPO_URL)}, set <b>Type</b> to <b>Integration</b>, and click <b>Add</b>.")
    bl("Search HACS for <b>Viper Dynamics</b>, open it, and click <b>Download</b>.")
    bl("Restart Home Assistant: <b>Settings → System</b>, three-dot menu (top right), <b>Restart Home Assistant</b>.")

    h2(f"{num}.3  Add your {name}")
    p(f"With the {name} powered on, open <b>Settings → Devices &amp; services</b>. Within a minute it "
      f"appears under <b>Discovered</b> as <b>{info.get('ha_name', name)} ({info['host']})</b>, with the Viper Dynamics "
      "logo. Click <b>Add</b>, then <b>Submit</b>.")
    p("To add it by hand instead, click <b>Add integration</b>, choose <b>Viper Dynamics</b>, and "
      f"enter {code(info['host'] + '.local')} or the IP address from the boot splash.")
    story.append(Spacer(1, 4))
    story.append(callout(
        "NOTE",
        "If it is not discovered, Home Assistant cannot see the device's network announcements. "
        "This happens when they are on different networks or VLANs, or when Home Assistant runs in "
        "Docker without host networking. Adding it by address always works.",
        ST,
    ))

    h2(f"{num}.4  What you can control")
    for line in info["controls"]:
        bl(line)
    story.append(Spacer(1, 4))
    story.append(callout(
        "TIP",
        "Set <b>Brightness</b> to 0 to turn the screen fully off, for example from a bedtime "
        "automation. " + _wake_text(info) + " An alarm still lights the screen while it rings.",
        ST,
    ))

    h2(f"{num}.5  Updates")
    p("Updates to the Viper Dynamics integration arrive through HACS and appear under "
      "<b>Settings → Updates</b>.")
    p(_firmware_text(info))


# ── quick start pointer ───────────────────────────────────────────────────────

def quickstart_pointer(c, g, x_right, y):
    """One line under the quick start's header block pointing to the manual.

    The quick start stays a one-page setup card; Home Assistant and other
    advanced features live in the user manual.
    """
    c.saveState()
    c.setFillColor(g["GOLD_DK"])
    c.setFont("Times-BoldItalic", 7)
    c.drawRightString(x_right, y, "Home Assistant & advanced features: see the user manual")
    c.restoreState()
