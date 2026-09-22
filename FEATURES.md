# Pomodoro 2.0

A lightweight, always-on-top sticky-note Pomodoro timer for Linux (Python + tkinter).

## Quick Start

- **Launch:** click the **Pomodoro Timer** icon on your Desktop (or search "Pomodoro" in the app menu).
- **Run from terminal:** `python3 "/home/saad/Pomodoro 2.0/pomodoro-sticky.py"`
- **Exit:** click the **×** button, or press **Escape**.

## Files

| File | Purpose |
|------|---------|
| `pomodoro-sticky.py` | The application itself |
| `pomodoro.desktop` | Desktop/app-menu launcher entry |

## Timing

- Cycle: **25 → 5 → 25 → 10 → 25 → 5 → 25** minutes (4 pomodoros per session).
- After the 4th pomodoro, a new session starts automatically (S1, S2, S3...).
- Drift-free countdown based on wall-clock time.

## Phase End Flow

- A **single beep** sounds when a phase ends.
- The window goes **blank** with only a white **Next ▶** button, while the background smoothly **cycles through RGB colors**.
- **Click anywhere** (or press Next) to start the next phase; the background instantly returns to its single dark color.

## Controls

| Control | Action |
|---------|--------|
| **Start / Pause** | Start or pause the current phase |
| **Resume** | Pause resumes exactly where you stopped (paused time is not counted) |
| **Reset** | Restart the whole session from the beginning |
| **×** | Exit the app (or press **Escape**) |
| **Top strip** | Drag the note anywhere on the screen |

## Display

- Frameless sticky-note sized **2" × 1.5"** (DPI-aware), pinned to the **top-left corner**, always-on-top.
- Shows phase (Work/Break), live `MM:SS` timer, pomodoro progress dots, and session counter.
- Timer font **auto-sizes** to fit the frame — nothing is clipped.

## Performance

- Pure Python + tkinter: ~0% CPU while running, ~17 MB RAM, **zero GPU** usage.
- RGB blink runs only during the phase-end wait and cancels instantly on click.

## Integration

- Clickable desktop launcher — **no terminal required**.
- Exits cleanly and leaves no background processes when closed.