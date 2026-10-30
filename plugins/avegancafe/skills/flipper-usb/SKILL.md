---
name: flipper-usb
description: Use when Kyle has his Flipper Zero plugged in over USB and wants an app built, installed, launched or debugged, or wants something read from, run on, or pressed on the Flipper — CLI commands, SD files, live logs, button presses, or talking to a GPIO board (ESP32 WiFi card, Marauder) through a probe app. Covers ufbt builds against the right firmware SDK, the serial-port rules that otherwise cause silent hangs, and the app-load errors that only show on the device.
---

# Flipper Zero over USB (Linux)

The Flipper shows up as `/dev/serial/by-id/usb-Flipper_Devices_Inc._Flipper_*` → `/dev/ttyACM0`.
Its CLI runs at 230400 baud. Apps are built with **ufbt** (`~/.local/bin/ufbt`, SDK in `~/.ufbt`).
App source lives in `~/workspace/<repo>` (e.g. `flipper-rat`, `flipper-wifi-analyzer`).

## The helper

`scripts/flipper_cli.py` (needs pyserial; system python has none, so always run it via uv):

```bash
F="uv run --no-project --with pyserial python -I ${CLAUDE_PLUGIN_ROOT}/skills/flipper-usb/scripts/flipper_cli.py"
$F port                                   # where it is, who holds the port
$F cli "info device" "loader info"        # any CLI commands; each stops at the prompt or 15 s
$F read /ext/apps_data/<app>/log.txt      # print a text file from the SD card (--out FILE to save)
$F press back down down ok                # button presses (KEY:long for long press)
$F logs 20 --open /ext/apps/GPIO/x.fap    # launch an app, then stream its FURI_LOG output 20 s
```

If `CLAUDE_PLUGIN_ROOT` is unset, use the script's path next to this file. It refuses to run if another process
holds the port and prints who, instead of hanging.

## Serial-port rules (each cost failed calls)

- **One process at a time.** A second reader, a stale background loop, or `minicom` holding
  `/dev/ttyACM0` makes every later command hang or return nothing. Check with
  `fuser /dev/ttyACM0` (or `$F port`) first.
- **Stop your own leftovers with `TaskStop <id>`**, not `pkill -f <pattern>`: a pattern that
  matches your own shell's command line kills the shell (exit 144). Killing other processes by
  PID gets refused by the auto-mode classifier anyway.
- **Hard-cap every read.** A reader that waits "until output goes quiet" never stops on a long
  `storage read` or a streaming `log`. The helper stops at the `>: ` prompt or a deadline.
- **No foreground `sleep`.** Wait with `timeout N tail -f /dev/null`, or run the wait as a
  background task and get notified.
- If the CLI seems dead but the port is free, send Ctrl-C (`\x03`) and a newline: something
  (usually `log`) is still streaming. The helper does this on connect.

## Build, install, launch

```bash
$F cli "info device"   # firmware.version + api.major/minor
ufbt                     # build -> dist/<appid>.fap; last lines show "Target: 7, API: <major>.<minor>"
ufbt launch              # copy to /ext/apps/<category>/ and start it
```

- **The SDK must match the firmware API.** If the build's API ≠ `info device`'s
  `firmware.api.major/minor`, the app won't load (`ApiTooNew`/`ApiTooOld`). Kyle runs official
  firmware; for a specific release:
  `ufbt update --hw-target=f7 --url=https://update.flipperzero.one/builds/firmware/<ver>/flipper-z-f7-sdk-<ver>.zip`
  (latest: `ufbt update --channel=release`). Check `~/.ufbt/current/ufbt_state.json`.
- **`ufbt launch` only says "Load failed".** Get the real reason with
  `$F cli "loader open /ext/apps/<cat>/<appid>.fap"`.
- **`MissingImports`** = the app calls a symbol the firmware doesn't export, often plain libc
  (`qsort` is not exported). Find it:
  ```bash
  API=~/.ufbt/current/sdk_headers/f7_sdk/targets/f7/api_symbols.csv
  ~/.ufbt/toolchain/x86_64-linux/bin/arm-none-eabi-nm -u dist/<appid>.fap | awk '{print $2}' |
    while read s; do grep -q -E "^(Function|Variable),\+,$s," "$API" || echo "MISSING $s"; done
  ```
  Replace it (e.g. insertion sort instead of `qsort`).
- **`sources=["*.c"]` in `application.fam` is recursive.** With a `core/` subfolder, also
  listing `"core/*.c"` compiles files twice (`multiple definition of ...`). A host-test
  `main()` under `tests/` gets pulled in too. Use `sources=["*.c", "!tests"]`.
- Host unit tests: keep pure logic in `core/` (no SDK headers) and build it with `cc` from a
  Makefile (`make test`), like `flipper-rat`.

## Driving the UI from the CLI

- `input send <key> short` **alone is ignored**: ViewDispatcher drops an event unless the key
  was pressed first. Send `press`, then `short` (or `long`), then `release` (the helper's
  `press` does this).
- Navigation is by count: from an app's first screen, `back` usually returns to its menu, then
  `down` ×N and `ok`. Read state back afterwards (a file the app wrote, `loader info`), since
  you can't see the screen.
- `loader info` says which app is running; `loader close` closes it (the app's exit path runs,
  so settings get saved).

## Files

- `$F read PATH` for text. `storage list <dir>` / `storage tree <dir>` / `storage stat <file>`
  via `$F cli`.
- Binary or large files: ufbt's own transfer script, which needs extra deps:
  ```bash
  cd ~/.ufbt/current/scripts && uv run --no-project --with pyserial --with colorlog --with heatshrink2 \
    python storage.py -p /dev/ttyACM0 receive /ext/<path> <local file>     # or: send <local> /ext/<path>
  ```
  Without `colorlog`/`heatshrink2` it dies on import. It also stalls if the CLI is mid-stream
  or another process holds the port; then fall back to `$F read` for text files.
- Put pulled app binaries and logs in the session scratchpad, never in the app repo
  (except deliberate backups).

## Live logs

`FURI_LOG_I/W/E` from an app go to the CLI `log` stream, at `log info` level or more verbose.
Open the app first (`loader open`), then stream (`log info` until Ctrl-C). `$F logs N --open FAP`
does both. Logs are only visible while streaming; nothing is buffered from before.

## Talking to a GPIO board (probe app)

To find out what a board on the GPIO header (ESP32 WiFi card, etc.) actually says, write a
throwaway FAP in the scratchpad rather than guessing a protocol:

1. `expansion_disable(furi_record_open(RECORD_EXPANSION))` **before**
   `furi_hal_serial_control_acquire(FuriHalSerialIdUsart)` (pins 13/14); `expansion_enable` after
   release. `FuriHalSerialIdLpuart` is pins 15/16.
2. If `!furi_hal_power_is_otg_enabled()`, call `furi_hal_power_enable_otg()` to power the board
   from 5 V, and wait ~1 s. Turn it off on exit only if you turned it on.
3. `furi_hal_serial_init(h, 115200)`, async RX callback → `furi_stream_buffer_send(..., 0)`
   (ISR context, no blocking), drain it in the app thread.
4. Send commands with gaps of 1 s or more, and write every received byte with a ms timestamp to
   `/ext/apps_data/<probe>/log.txt`. `ufbt launch`, wait, then `$F read` the log.
5. Remove the probe afterwards: `storage remove` its `.fap` and its `apps_data` folder. Those
   are the probe's own files; never delete Kyle's app data.

**ESP32 Marauder** findings, from the Hackitsune ESP32-C5 running Marauder v1.17.0 on USART at
115200:
- `info` prints `Firmware: Marauder`, `Version: v1.17.0` and `Hardware: ...`.
- A command sent while the card is still printing gets echoed but silently dropped. Wait about
  1 s, and confirm the start line, e.g. `StartingBeacon sniff`.
- v1.17 has no `scanap`; use `sniffbeacon`. It prints every beacon as
  `<rssi> Ch: <ch> <bssid> ESSID: <ssid>`, and the prompt `> ` can prefix a line.
- Its own channel hopping obeys the saved `ChanHop` setting, which is off on Kyle's card.
  Hop from the app with `channel -s N` instead (works on 5 GHz), and don't change the card's
  settings.
- `Ch:` is the channel the radio was on, so a 2.4 GHz AP also shows up on neighbouring
  channels. Keep the strongest reading per AP.

Check the Marauder source at the matching tag
(`github.com/justcallmekoko/ESP32Marauder`, `esp32_marauder/CommandLine.{h,cpp}`) before
assuming a command exists.
