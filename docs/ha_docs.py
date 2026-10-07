"""Home Assistant pages for Viper Dynamics user manuals and quick starts.

Shared by every product's gen_docs.py (copy this file next to it). The
generator passes its own helpers and colours, so the pages match each
product's look:

    from ha_docs import manual_section, quickstart_page
    manual_section("9", h1, h2, p, bl, story, callout, ST, HA_INFO)
    quickstart_page(c, globals(), HA_INFO)   # after the first page is drawn

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


# ── quick start page 2 ────────────────────────────────────────────────────────

def _pick(g, *names):
    for n in names:
        if n in g:
            return g[n]
    raise KeyError(names[0])


def quickstart_page(c, g, info):
    """Draw a Home Assistant page as page 2 of a quick-start canvas."""
    from reportlab.lib.colors import HexColor, white

    PW, PH, ML, MR, CW = g["PW"], g["PH"], g["ML"], g["MR"], g["CW"]
    HEADER, CARD, GOLD, GOLD_DIM, GOLD_DK = g["HEADER"], g["CARD"], g["GOLD"], g["GOLD_DIM"], g["GOLD_DK"]
    PARCH, INK, MUTED, PAGE = g["PARCH"], g["INK"], g["MUTED"], g["PAGE"]
    ACCENT = _pick(g, "PORTAL", "FEL")
    ACCENT_DK = _pick(g, "PORTAL_DK", "FEL_DIM")
    GOOD = _pick(g, "GRASS", "ALLIANCE")
    WARN = _pick(g, "WARN_RED", "HORDE")
    rounded, section_bar, wrap_text = g["rounded"], g["section_bar"], g["wrap_text"]
    name = info["name"]

    c.showPage()
    c.setFillColor(PAGE)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)

    c.setFillColor(HEADER)
    c.setFont("Times-Bold", 22)
    c.drawString(ML, PH - 36, name.upper())
    c.setFillColor(ACCENT_DK)
    c.setFont("Times-Bold", 9)
    c.drawString(ML, PH - 50, "HOME ASSISTANT")
    c.setFillColor(GOLD_DK)
    c.setFont("Times-Italic", 13)
    c.drawString(ML, PH - 68, "Smart Home Setup")
    c.setFillColor(MUTED)
    c.setFont("Times-Roman", 8)
    c.drawString(ML, PH - 82, "Viper Dynamics LLC  ·  Works with Home Assistant " + HA_MIN + "+ via HACS")
    c.setFillColor(HEADER)
    c.setFont("Times-Bold", 8)
    c.drawRightString(PW - MR, PH - 40, "Local control, no cloud")
    c.setFillColor(MUTED)
    c.setFont("Times-Roman", 6.5)
    c.drawRightString(PW - MR, PH - 52, "Firmware " + info["min_fw"] + " or newer")
    c.drawRightString(PW - MR, PH - 62, "Full details: " + info["manual"])

    rule_y = PH - 96
    c.setStrokeColor(ACCENT_DK)
    c.setLineWidth(1.4)
    c.line(ML, rule_y, PW - MR, rule_y)
    y = rule_y - 12

    def body(text, x, y, size=8, leading=10.5, color=INK, width=None, font="Times-Roman"):
        c.setFillColor(color)
        c.setFont(font, size)
        for ln in wrap_text(c, text, font, size, width or (CW - 8)):
            c.drawString(x, y, ln)
            y -= leading
        return y

    def bullets(items, y, size=8.6, leading=11.2):
        for b in items:
            c.setFillColor(GOLD_DIM)
            c.circle(ML + 10, y + 2, 1.6, fill=1, stroke=0)
            y = body(b, ML + 16, y, size=size, leading=leading, width=CW - 22) - 2
        return y

    y = section_bar(c, y, "1  ·  BEFORE YOU START")
    y -= 14
    y = bullets([
        f"Home Assistant {HA_MIN} or newer on the same network as the {name}.",
        f"HACS (Home Assistant Community Store) installed. Instructions: {HACS_URL}",
        f"{name} firmware {info['min_fw']} or newer (shown on the boot splash), already on your home Wi-Fi.",
    ], y)
    y -= 6

    y = section_bar(c, y, "2  ·  INSTALL THE VIPER DYNAMICS INTEGRATION  (once per Home Assistant)")
    y -= 10
    rounded(c, ML, y - 30, CW, 30, 3, HexColor("#101820"), ACCENT, 1.1)
    c.setFillColor(PARCH)
    c.setFont("Times-Bold", 8)
    c.drawString(ML + 10, y - 12, "Custom repository:")
    c.setFillColor(GOLD)
    c.setFont("Courier-Bold", 10)
    c.drawString(ML + 100, y - 12, REPO_URL)
    c.setFillColor(PARCH)
    c.setFont("Times-Bold", 8)
    c.drawString(ML + 10, y - 24, "Type:")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 8)
    c.drawString(ML + 100, y - 24, "Integration")
    y -= 42
    steps = [
        "1.  Open HACS in Home Assistant.",
        "2.  Three-dot menu (top right) → Custom repositories.",
        "3.  Paste the address above, choose Integration, click Add.",
        "4.  Search HACS for Viper Dynamics → Download.",
        "5.  Settings → System → three-dot menu → Restart Home Assistant.",
    ]
    for s in steps:
        y = body(s, ML + 10, y, size=9, leading=13)
    y -= 10

    y = section_bar(c, y, f"3  ·  ADD YOUR {name.upper()}")
    y -= 8
    col_w = (CW - 8) / 2
    col_h = 108
    ax = ML + col_w + 8
    cards = [
        (ML, GOOD, "It finds it for you  (recommended)", [
            f"Power on the {name}.",
            "Settings → Devices & services.",
            f"Under Discovered: {info.get('ha_name', name)} ({info['host']}).",
            "Click Add, then Submit. Done.",
        ]),
        (ax, HexColor("#1a3a5c"), "Or add it by address", [
            "Settings → Devices & services.",
            "Add integration → Viper Dynamics.",
            f"Enter {info['host']}.local, or the IP",
            "from the boot splash. Submit.",
        ]),
    ]
    for x, colour, title, lines in cards:
        rounded(c, x, y - col_h, col_w, col_h, 4, CARD, colour, 1.2)
        c.setFillColor(colour)
        c.rect(x, y - 16, col_w, 16, fill=1, stroke=0)
        c.setFillColor(PARCH)
        c.setFont("Times-Bold", 8)
        c.drawCentredString(x + col_w / 2, y - 12, title)
        yy = y - 32
        c.setFont("Times-Roman", 8.8)
        for i, s in enumerate(lines, 1):
            for ln in wrap_text(c, f"{i}. {s}", "Times-Roman", 8.8, col_w - 16):
                c.drawString(x + 8, yy, ln)
                yy -= 13
    y -= col_h + 12

    y = section_bar(c, y, "4  ·  WHAT YOU CAN CONTROL")
    y -= 12
    plain = [s.replace("<b>", "").replace("</b>", "").replace("&amp;", "&") for s in info["controls"]]
    y = bullets(plain, y, size=8.6, leading=11.2)
    y -= 2
    rounded(c, ML, y - 32, CW, 32, 3, HexColor("#142014"), GOOD, 1.1)
    c.setFillColor(HexColor("#85ea2d"))
    c.setFont("Times-Bold", 8.5)
    c.drawString(ML + 8, y - 13, "Screen off:")
    c.setFillColor(PARCH)
    c.setFont("Times-Roman", 8.4)
    wake = "tap the screen or raise brightness" if info.get("wake") == "touch" else "raise brightness"
    c.drawString(ML + 64, y - 13, f"set Brightness to 0 (great for bedtime automations). To turn it back on, {wake}.")
    c.drawString(ML + 64, y - 25, "A ringing alarm still lights the screen.")
    y -= 44

    y = section_bar(c, y, "5  ·  IF IT DOESN'T SHOW UP")
    y -= 12
    y = bullets([
        "Restart Home Assistant after installing the integration; discovery starts after the restart.",
        f"Home Assistant and the {name} must be on the same network (not a guest network or another VLAN).",
        "Home Assistant in Docker needs host networking to see discovered devices. Or add the device by address.",
        f"Check the firmware: {info['min_fw']} or newer is required. Update it from the web console first.",
    ], y)

    c.setFillColor(MUTED)
    c.setFont("Times-Italic", 7)
    c.drawString(ML, 16, "Integration: " + REPO_SHORT + "  ·  Support: viperdynamics.llc/support")
    c.drawRightString(PW - MR, 16, "© Viper Dynamics LLC")
    c.setFont("Times-Roman", 6.5)
    c.drawCentredString(PW / 2, 7, "Home Assistant is a trademark of its owner. Viper Dynamics is not affiliated with Home Assistant.")
