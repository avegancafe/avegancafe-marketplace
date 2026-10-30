#!/usr/bin/env python3
"""Drive a USB-connected Flipper Zero's CLI with hard time limits.

Run with:  uv run --no-project --with pyserial python -I flipper_cli.py <command> ...

  port                     where the Flipper is and which processes hold its port
  cli "CMD" ["CMD" ...]    run CLI commands, print each one's output
  press KEY [KEY ...]      press buttons: up down left right ok back (KEY:long for a long press)
  read PATH [--out FILE]   print (or save) a text file from the SD card, e.g. /ext/apps_data/x/log.txt
  logs SECONDS [--open FAP]  stream `log info` for SECONDS, optionally after `loader open FAP`

Every read stops at the CLI prompt or a hard deadline, so a busy port or endless output
can't hang the caller. It refuses to open a port another process already holds.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import time

import serial  # type: ignore[import-untyped]

BAUD = 230400
PROMPT = b"\r\n>: "
KEYS = {"up", "down", "left", "right", "ok", "back"}


def find_port():
    ids = sorted(glob.glob("/dev/serial/by-id/usb-Flipper_Devices*"))
    if ids:
        return os.path.realpath(ids[0])
    acm = sorted(glob.glob("/dev/ttyACM*"))
    return acm[0] if acm else None


def holders(port):
    """PIDs with the port open (fuser prints them on stdout)."""
    try:
        out = subprocess.run(["fuser", port], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return []
    return [p for p in out.split() if p.isdigit()]


def describe(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().replace(b"\0", b" ").decode(errors="replace").strip()
    except OSError:
        return "?"


class Flipper:
    def __init__(self, port):
        self.s = serial.Serial(port, BAUD, timeout=0.2)
        self.s.reset_input_buffer()
        # Ctrl-C ends anything still streaming (e.g. a `log` left running), then sync to a prompt.
        self.s.write(b"\x03\r\n")
        self._until_prompt(3)

    def _until_prompt(self, limit):
        out = b""
        deadline = time.time() + limit
        while time.time() < deadline:
            out += self.s.read(4096)
            if out.endswith(PROMPT) or out.rstrip(b" ").endswith(b">:"):
                break
        return out

    def run(self, cmd, limit=15.0):
        """Runs one CLI command; returns its output without the echo and prompt."""
        self.s.write(cmd.encode() + b"\r\n")
        raw = self._until_prompt(limit)
        text = raw.decode(errors="replace").replace("\r\n", "\n")
        if text.startswith(cmd):
            text = text[len(cmd):]
        return re.sub(r"\n*>: *$", "", text).strip("\n")

    def stream(self, seconds):
        deadline = time.time() + seconds
        while time.time() < deadline:
            chunk = self.s.read(4096)
            if chunk:
                sys.stdout.write(chunk.decode(errors="replace").replace("\r\n", "\n"))
                sys.stdout.flush()
        self.s.write(b"\x03")

    def close(self):
        self.s.close()


def open_flipper():
    port = find_port()
    if not port:
        sys.exit("No Flipper found (no /dev/serial/by-id/usb-Flipper_Devices* or /dev/ttyACM*).")
    busy = holders(port)
    if busy:
        lines = "\n".join(f"  {p}: {describe(p)}" for p in busy)
        sys.exit(f"{port} is held by:\n{lines}\nStop that process first (only one may use the port).")
    return Flipper(port)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("port")
    c = sub.add_parser("cli")
    c.add_argument("commands", nargs="+")
    c.add_argument("--timeout", type=float, default=15.0, help="seconds per command")
    p = sub.add_parser("press")
    p.add_argument("keys", nargs="+")
    r = sub.add_parser("read")
    r.add_argument("path")
    r.add_argument("--out")
    lg = sub.add_parser("logs")
    lg.add_argument("seconds", type=float)
    lg.add_argument("--open", dest="fap")
    a = ap.parse_args()

    if a.cmd == "port":
        port = find_port()
        print(f"port: {port}")
        for pid in holders(port) if port else []:
            print(f"held by {pid}: {describe(pid)}")
        return

    f = open_flipper()
    try:
        if a.cmd == "cli":
            for cmd in a.commands:
                print(f"=== {cmd}")
                print(f.run(cmd, a.timeout))
        elif a.cmd == "press":
            for k in a.keys:
                key, _, kind = k.partition(":")
                kind = kind or "short"
                if key not in KEYS or kind not in ("short", "long"):
                    sys.exit(f"bad key {k!r}: use {sorted(KEYS)} with optional :long")
                # ViewDispatcher ignores a short/long event without the press before it.
                for t in ("press", kind, "release"):
                    err = f.run(f"input send {key} {t}", 3)
                    if err:
                        sys.exit(f"input send {key} {t}: {err}")
                time.sleep(0.15)
        elif a.cmd == "read":
            out = f.run(f"storage read {a.path}", 30)
            m = re.match(r"Size: (\d+)\n", out)
            if not m:
                sys.exit(out or f"no output reading {a.path}")
            body = out[m.end():]
            if a.out:
                with open(a.out, "w") as fh:
                    fh.write(body)
                print(f"saved {len(body)} chars to {a.out} (Flipper says {m.group(1)} bytes)")
            else:
                print(body)
        elif a.cmd == "logs":
            if a.fap:
                print(f.run(f"loader open {a.fap}", 5))
            f.s.write(b"log info\r\n")
            f.stream(a.seconds)
    finally:
        f.close()


if __name__ == "__main__":
    main()
