#!/usr/bin/env python3
"""Pomodoro sticky note timer - always on top, top-left corner, ultra lightweight."""

import tkinter as tk
import tkinter.font as tkfont
import time

# Cycle: 25 + 5 + 25 + 10 + 25 + 5 + 25 (minutes). 4 pomodoros per session.
SCHEDULE = [
    (25, 'Work'),
    (5, 'Break'),
    (25, 'Work'),
    (10, 'Break'),
    (25, 'Work'),
    (5, 'Break'),
    (25, 'Work'),
]

BG = '#16213e'
FG = '#eeeeee'
WORK = '#e94560'
BREAK = '#4ecca3'
DOT_ON = '#e94560'
DOT_CUR = '#4ecca3'
DOT_OFF = '#333333'

root = tk.Tk()
root.title('Pomodoro')
root.configure(bg=BG)

# Frameless + always on top + skip taskbar = sticky-note behaviour.
root.overrideredirect(True)
root.attributes('-topmost', True)
root.attributes('-alpha', 0.97)
try:
    root.attributes('-type', 'utility')
except tk.TclError:
    pass

# Size: 2" x 1.5" based on screen DPI.
dpi = root.winfo_fpixels('1i')
width = max(170, int(2 * dpi))
height = max(110, int(1.5 * dpi))
root.geometry(f'{width}x{height}')

state = {
    'step': 0,
    'end_ts': None,
    'running': False,
    'waiting': False,
    'session': 1,
    'paused_remaining': None,
}

hue = 0.0
blink_id = None

def quit_app(_event=None):
    root.destroy()

# ---------------------------------------------------------------- UI
grip = tk.Frame(root, bg=BG, cursor='fleur', height=8)
grip.pack(fill=tk.X)
grip.pack_propagate(False)

main = tk.Frame(root, bg=BG)
main.pack(fill=tk.BOTH, expand=True)

top = tk.Frame(main, bg=BG)
top.pack(fill=tk.X, padx=8, pady=(2, 0))

phase_label = tk.Label(top, text='Work', bg=BG, fg=WORK, font=('DejaVu Sans', 9, 'bold'))
phase_label.pack(side=tk.LEFT)

session_label = tk.Label(top, text='S1', bg=BG, fg=FG, font=('DejaVu Sans', 9))
session_label.pack(side=tk.LEFT, padx=8)

close_btn = tk.Button(top, text='\u00d7', bg=BG, fg='#999999', relief=tk.FLAT,
                      activebackground=BG, activeforeground='#ffffff',
                      bd=0, highlightthickness=0, padx=3, pady=0,
                      font=('DejaVu Sans', 9, 'bold'), command=quit_app)
close_btn.pack(side=tk.RIGHT)

# Timer on its own line.
time_row = tk.Frame(main, bg=BG)
time_row.pack(fill=tk.X, padx=8, pady=(0, 0))

time_label = tk.Label(time_row, text='25:00', bg=BG, fg=FG)
time_label.pack()

btn_font = tkfont.Font(family='DejaVu Sans', size=9, weight='bold')
btn_pause_text = 'Pause'
btn_start_text = 'Start'

time_font = tkfont.Font(family='DejaVu Sans Mono', weight='bold')
avail_w = width - 16
avail_h = height - 80
size = 1
while size < 200:
    time_font.configure(size=size + 1)
    if time_font.measure('25:00') > avail_w or time_font.metrics('linespace') > avail_h:
        break
    size += 1
time_font.configure(size=size)
time_label.config(font=time_font)

# Start/Pause and Reset buttons on one line.
btns = tk.Frame(main, bg=BG)
btns.pack(pady=(2, 4))

start_btn = tk.Button(btns, text=btn_start_text, bg=WORK, fg='white', relief=tk.FLAT,
                      bd=0, highlightthickness=0, padx=10, pady=2, font=btn_font,
                      activebackground=WORK, activeforeground='white',
                      command=lambda: toggle())
start_btn.pack(side=tk.LEFT, padx=6)

reset_btn = tk.Button(btns, text='Reset', bg='#555555', fg='white', relief=tk.FLAT,
                      bd=0, highlightthickness=0, padx=12, pady=2, font=btn_font,
                      activebackground='#666666', activeforeground='white',
                      command=lambda: reset())
reset_btn.pack(side=tk.LEFT, padx=6)

# Pomodoro progress dots.
dots = tk.Frame(main, bg=BG)
dots.pack(pady=(0, 0))
dot_widgets = []
for _ in range(4):
    d = tk.Label(dots, text='\u25cf', bg=BG, fg=DOT_OFF, font=('DejaVu Sans', 9))
    d.pack(side=tk.LEFT, padx=4)
    dot_widgets.append(d)

# Blank RGB-wait overlay: only a Next button.
wait_frame = tk.Frame(main, bg=BG)
wait_frame.pack(fill=tk.BOTH, expand=True)
wait_frame.pack_forget()

next_btn = tk.Button(wait_frame, text='Next \u25b6', bg='#ffffff', fg='#111111',
                     relief=tk.FLAT, bd=0, highlightthickness=0,
                     font=('DejaVu Sans', 14, 'bold'),
                     activebackground='#dddddd', activeforeground='#111111',
                     command=lambda: resume_next())
next_btn.pack(expand=True)

# ---------------------------------------------------------------- drag
_drag = {'x': 0, 'y': 0}

def start_drag(event):
    _drag['x'] = event.x_root - root.winfo_x()
    _drag['y'] = event.y_root - root.winfo_y()

def do_drag(event):
    root.geometry(f'+{event.x_root - _drag["x"]}+{event.y_root - _drag["y"]}')

grip.bind('<Button-1>', start_drag)
grip.bind('<B1-Motion>', do_drag)

root.bind('<Escape>', quit_app)

# ---------------------------------------------------------------- logic
def set_bg(col):
    for w in (root, grip, main, top, time_row, dots, btns, wait_frame):
        w.config(bg=col)
    close_btn.config(bg=col, activebackground=col)
    start_btn.config(activebackground=col if state['waiting'] else
                     (BREAK if state['running'] else WORK))

def show_wait():
    top.pack_forget()
    time_row.pack_forget()
    btns.pack_forget()
    dots.pack_forget()
    wait_frame.pack(fill=tk.BOTH, expand=True)

def show_normal():
    wait_frame.pack_forget()
    top.pack(fill=tk.X, padx=8, pady=(2, 0))
    time_row.pack(fill=tk.X, padx=8, pady=(0, 0))
    btns.pack(pady=(2, 4))
    dots.pack(pady=(0, 0))

def hsv_to_hex(h, s=0.9, v=0.7):
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t),
               (p, q, v), (t, p, v), (v, p, q)][i]
    return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

def blink_step():
    global hue, blink_id
    if not state['waiting']:
        return
    hue = (hue + 0.012) % 1.0
    set_bg(hsv_to_hex(hue))
    blink_id = root.after(40, blink_step)

def stop_blink():
    global blink_id
    if blink_id is not None:
        root.after_cancel(blink_id)
        blink_id = None

def update_ui(remaining_min, step, pomo, session):
    m = int(remaining_min // 60)
    s = int(remaining_min % 60)
    time_label.config(text=f'{m:02d}:{s:02d}')

    kind = SCHEDULE[step][1]
    phase_label.config(text=kind, fg=WORK if kind == 'Work' else BREAK)

    session_label.config(text=f'S{session}')

    for i, d in enumerate(dot_widgets, start=1):
        if i < pomo or (i == pomo and kind == 'Break'):
            d.config(fg=DOT_ON)
        elif i == pomo and kind == 'Work':
            d.config(fg=DOT_CUR)
        else:
            d.config(fg=DOT_OFF)

def advance():
    state['step'] += 1
    if state['step'] >= len(SCHEDULE):
        state['step'] = 0
        state['session'] += 1
        session_label.config(text=f'S{state["session"]}')

def pomo_for(step):
    return sum(1 for _mn, _kind in SCHEDULE[:step + 1] if _kind == 'Work')

def begin_wait():
    """Phase finished: blank window, blink RGB until any click."""
    state['running'] = False
    state['waiting'] = True
    show_wait()
    root.bell()
    set_bg(BG)
    blink_step()

def resume_next(_event=None):
    if not state['waiting']:
        return
    stop_blink()
    state['waiting'] = False
    advance()
    state['end_ts'] = time.monotonic() + SCHEDULE[state['step']][0] * 60
    state['running'] = True
    show_normal()
    set_bg(BG)
    start_btn.config(text=btn_pause_text, bg=BREAK)
    update_ui(SCHEDULE[state['step']][0] * 60, state['step'],
              pomo_for(state['step']), state['session'])
    tick()

def tick():
    if not state['running']:
        return
    remaining = state['end_ts'] - time.monotonic()
    if remaining <= 0:
        begin_wait()
        return
    update_ui(remaining, state['step'], pomo_for(state['step']), state['session'])
    root.after(250, tick)

def toggle():
    if state['waiting']:
        resume_next()
        return
    if state['running']:
        state['running'] = False
        state['paused_remaining'] = state['end_ts'] - time.monotonic()
        start_btn.config(text=btn_start_text, bg=WORK)
    else:
        state['running'] = True
        if state['end_ts'] is None:
            state['end_ts'] = time.monotonic() + SCHEDULE[state['step']][0] * 60
        elif state.get('paused_remaining') is not None:
            state['end_ts'] = time.monotonic() + state['paused_remaining']
        start_btn.config(text=btn_pause_text, bg=BREAK)
        tick()

def reset():
    if state['waiting']:
        resume_next()
        return
    state['running'] = False
    state['step'] = 0
    state['end_ts'] = None
    state['paused_remaining'] = None
    state['session'] = 1
    set_bg(BG)
    update_ui(SCHEDULE[0][0] * 60, 0, 1, 1)
    start_btn.config(text=btn_start_text, bg=WORK)

# Any click on the window starts the next phase while waiting.
root.bind('<Button-1>', resume_next)

reset()
# Anchor top-left with a small margin.
root.geometry(f'+8+8')
root.mainloop()