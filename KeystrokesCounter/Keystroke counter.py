"""
Keystroke Counter - counts one chosen key system-wide, even while you work in other apps.

- Counts only the key you pick. Nothing else is read, stored or sent anywhere.
- Saves after every press, so the count survives shutdowns and crashes.
- Data file: ~/.keystroke_counter.json  (also keeps a per-day history)

Setup:   pip install pynput
Run:     python keystroke_counter.py
"""

import json
import os
import queue
import tempfile
import tkinter as tk
from datetime import date
from pathlib import Path

from pynput import keyboard

DATA_FILE = Path.home() / ".keystroke_counter.json"
DEFAULTS = {"key": "space", "label": "Space", "count": 0, "daily": {}}


# ---------- storage ----------
def load():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    except (OSError, ValueError):
        return dict(DEFAULTS, daily={})


def save(data):
    """Write to a temp file, then swap it in, so a power cut can't corrupt the save."""
    try:
        fd, tmp = tempfile.mkstemp(dir=str(DATA_FILE.parent), suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, DATA_FILE)
    except OSError:
        pass


# ---------- key helpers ----------
def key_id(key):
    if isinstance(key, keyboard.KeyCode):
        if key.char:
            return key.char.lower()
        return "vk%s" % key.vk
    return getattr(key, "name", str(key))


def key_label(key):
    ident = key_id(key)
    if ident == "space":
        return "Space"
    return ident.upper() if len(ident) == 1 else ident.replace("_", " ").title()


# ---------- app ----------
class App:
    def __init__(self):
        self.data = load()
        self.events = queue.Queue()
        self.down = set()
        self.listening = False

        self.root = tk.Tk()
        self.root.title("Key counter")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)  # X minimizes, keeps counting

        pad = {"padx": 14}
        self.key_lbl = tk.Label(self.root, font=("Helvetica", 12, "bold"), bg="#f2b705", fg="#2a1f00", padx=12, pady=4)
        self.key_lbl.pack(pady=(14, 0), **pad)
        self.count_lbl = tk.Label(self.root, font=("Helvetica", 44, "bold"))
        self.count_lbl.pack(**pad)
        self.today_lbl = tk.Label(self.root, font=("Helvetica", 10), fg="#5b6b80")
        self.today_lbl.pack(**pad)

        row = tk.Frame(self.root)
        row.pack(pady=12, **pad)
        tk.Button(row, text="Reset", width=7, command=self.reset).grid(row=0, column=0, padx=3)
        self.change_btn = tk.Button(row, text="Change key", width=9, command=self.toggle_listen)
        self.change_btn.grid(row=0, column=1, padx=3)
        tk.Button(row, text="Quit", width=5, command=self.quit).grid(row=0, column=2, padx=3)

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.daemon = True
        self.listener.start()

        self.refresh()
        self.poll()

    # runs on the listener thread: only queue things, never touch the UI here
    def on_press(self, key):
        ident = key_id(key)
        if ident in self.down:  # ignore auto-repeat while the key is held
            return
        self.down.add(ident)
        self.events.put((ident, key_label(key)))

    def on_release(self, key):
        self.down.discard(key_id(key))

    def poll(self):
        changed = False
        while True:
            try:
                ident, label = self.events.get_nowait()
            except queue.Empty:
                break
            if self.listening:
                self.data.update(key=ident, label=label, count=0)
                self.listening = False
                changed = True
            elif ident == self.data["key"]:
                today = date.today().isoformat()
                self.data["count"] += 1
                self.data["daily"][today] = self.data["daily"].get(today, 0) + 1
                changed = True
        if changed:
            save(self.data)
            self.refresh()
        self.root.after(50, self.poll)

    def refresh(self):
        if self.listening:
            self.key_lbl.config(text="Press a key...", bg="#c7d2de", fg="#14233a")
            self.change_btn.config(text="Cancel")
        else:
            self.key_lbl.config(text=self.data["label"], bg="#f2b705", fg="#2a1f00")
            self.change_btn.config(text="Change key")
        self.count_lbl.config(text="{:,}".format(self.data["count"]))
        today = self.data["daily"].get(date.today().isoformat(), 0)
        self.today_lbl.config(text="Today: {:,}".format(today))

    def reset(self):
        self.data["count"] = 0
        save(self.data)
        self.refresh()

    def toggle_listen(self):
        self.listening = not self.listening
        self.refresh()

    def quit(self):
        save(self.data)
        self.listener.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()