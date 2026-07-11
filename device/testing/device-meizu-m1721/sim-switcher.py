#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SIM switcher — a single small Adwaita app for meizu-m1721.

Replaces the earlier two bare app-grid launchers (SIM 1 / SIM 2) with one
consolidated window: shows the currently registered operator and lets the
user switch the active SIM with one tap. Runs `pkexec sim-select <1|2>`
under the hood (same polkit rule as before) and reports the result inline
instead of via desktop notifications. Only the switch action needs root
(via pkexec) - reading status uses unprivileged `mmcli`, since the qmicli
UIM card-status query sim-select itself uses needs root and isn't worth an
auth prompt just to open the app.
"""
import subprocess
import threading

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk


def current_operator():
    try:
        out = subprocess.run(
            ["mmcli", "-m", "any"], capture_output=True, text=True, timeout=5
        ).stdout
        for line in out.splitlines():
            if "operator name" in line.lower():
                return line.split(":", 1)[-1].strip()
    except Exception:
        pass
    return None


class SimSwitcherWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="SIM")
        self.set_default_size(360, 300)

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar.add_top_bar(header)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18,
            margin_top=24,
            margin_bottom=24,
            margin_start=18,
            margin_end=18,
        )

        self.status = Adw.StatusPage(
            icon_name="network-cellular-symbolic",
            title="Определение активной SIM…",
        )
        box.append(self.status)

        group = Adw.PreferencesGroup(title="Переключить активную SIM")
        self.row1 = Adw.ActionRow(title="SIM 1")
        btn1 = Gtk.Button(label="Активировать", valign=Gtk.Align.CENTER)
        btn1.add_css_class("suggested-action")
        btn1.connect("clicked", lambda *_: self.switch_to("1"))
        self.row1.add_suffix(btn1)
        group.add(self.row1)

        self.row2 = Adw.ActionRow(title="SIM 2")
        btn2 = Gtk.Button(label="Активировать", valign=Gtk.Align.CENTER)
        btn2.add_css_class("suggested-action")
        btn2.connect("clicked", lambda *_: self.switch_to("2"))
        self.row2.add_suffix(btn2)
        group.add(self.row2)

        box.append(group)

        note = Gtk.Label(
            label=(
                "На mainline-стеке активна только одна SIM за раз "
                "(нет полноценного DSDS)."
            ),
            wrap=True,
        )
        note.add_css_class("dim-label")
        note.add_css_class("caption")
        box.append(note)

        toolbar.set_content(box)
        self.set_content(toolbar)

        self.refresh_status()

    def refresh_status(self):
        def work():
            op = current_operator()
            GLib.idle_add(self.apply_status, op)

        threading.Thread(target=work, daemon=True).start()

    def apply_status(self, op):
        if op:
            title = f"Активный оператор: {op}"
        else:
            title = "Нет активной регистрации в сети"
        self.status.set_title(title)
        return False

    def switch_to(self, slot):
        self.status.set_title(f"Переключаю на SIM {slot}…")

        def work():
            try:
                out = subprocess.run(
                    ["pkexec", "/usr/bin/sim-select", slot],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                ok = out.returncode == 0
                msg = (out.stdout or out.stderr).strip()
            except Exception as e:
                ok, msg = False, str(e)
            GLib.idle_add(self.report_result, slot, ok, msg)

        threading.Thread(target=work, daemon=True).start()

    def report_result(self, slot, ok, msg):
        if ok:
            self.status.set_title(f"SIM {slot} активна")
        else:
            self.status.set_title(f"SIM {slot}: ошибка")
        self.status.set_description(msg or None)
        return False


class SimSwitcherApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.postmarketos.meizu-m1721.SimSwitcher")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = SimSwitcherWindow(self)
        win.present()


if __name__ == "__main__":
    SimSwitcherApp().run()
