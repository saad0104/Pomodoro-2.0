# Pomodoro 2.0

A lightweight, always-on-top sticky-note Pomodoro timer for Linux, built with Python and tkinter.

## Features

- Always-on-top sticky-note sized window (DPI-aware), pinned to the top-left corner
- Cycle: 25 → 5 → 25 → 10 → 25 → 5 → 25 min (4 pomodoros per session)
- Drift-free wall-clock countdown, pause/resume, reset, and session counter
- End-of-phase: beep, blank window with RGB color cycling, click anywhere to start the next phase
- Ultra-lightweight: ~0% CPU, ~17 MB RAM, no GPU usage

## Requirements

- Python 3 with tkinter (usually `python3-tk` on Debian/Ubuntu)

## Usage

```bash
python3 "pomodoro-sticky.py"
```

Or launch from your app menu/desktop via the included `pomodoro.desktop` launcher (no terminal required).

| Control | Action |
|---------|--------|
| **Start / Pause** | Start or pause the current phase |
| **Reset** | Restart the whole session |
| **× / Escape** | Exit the app |
| **Top strip** | Drag the note anywhere on screen |

## Files

| File | Purpose |
|------|---------|
| `pomodoro-sticky.py` | The application |
| `pomodoro.desktop` | Desktop launcher entry |
