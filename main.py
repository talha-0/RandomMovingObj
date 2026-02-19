import tkinter as tk
from tkinter import colorchooser
import turtle
import random
import time
import math

# ---------- Config (defaults) ----------
BG_COLOR = "black"
DOT_COLOR = "cyan"
STEP_SIZE = 3.0
FRAME_DELAY_MS = 16
PAUSE_ON_TURN = 0.35
MIN_DISTANCE = 100
MAX_DISTANCE = 600
EDGE_MARGIN = 15
REDIRECT_STEP = 150

# ---------- App / UI ----------
class RandomDotApp:
    def __init__(self, root):
        self.root = root
        root.title("Random Moving Dot — Tkinter + Turtle")

        # Top-level layout: left = canvas, right = controls
        self.left_frame = tk.Frame(root)
        self.right_frame = tk.Frame(root, padx=8, pady=8)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the Tkinter Canvas for turtle
        self.canvas_widget = tk.Canvas(self.left_frame, bg=BG_COLOR)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Create turtle screen & turtle on that canvas
        self.screen = turtle.TurtleScreen(self.canvas_widget)
        self.screen.bgcolor(BG_COLOR)
        self.screen.tracer(0)

        self.dot = turtle.RawTurtle(self.screen)
        self._configure_dot()

        # Animation bounds (will be updated on resize)
        self.max_x = 0
        self.max_y = 0
        self._update_bounds()

        # Internal animation state
        self.state = {
            "target_angle": None,
            "remaining_distance": 0.0,
            "paused_until": 0.0,
            "is_redirecting": False,
            "running": False,
            "step_size": STEP_SIZE,
            "frame_delay_ms": FRAME_DELAY_MS
        }

        # Build controls
        self._build_controls()

        # Bind resize event to recalc bounds
        self.canvas_widget.bind("<Configure>", self._on_canvas_configure)

        # Initialize movement
        a, d = self._pick_new_direction_and_distance()
        self._start_new_movement(a, d)

    # ----- turtle dot appearance -----
    def _configure_dot(self):
        self.dot.hideturtle()
        self.dot.shape("circle")
        # turtle uses shapesize(stretch_wid, stretch_len). radius approximated by stretch.
        self.dot.shapesize(1)  # baseline, tweak with dot size control
        self.dot.color(DOT_COLOR)
        self.dot.penup()
        self.dot.speed(0)
        self.dot.showturtle()

    # ----- bounds/resize -----
    def _update_bounds(self):
        width = max(self.canvas_widget.winfo_width(), 1)
        height = max(self.canvas_widget.winfo_height(), 1)
        self.max_x = width / 2.0 - EDGE_MARGIN
        self.max_y = height / 2.0 - EDGE_MARGIN

    def _on_canvas_configure(self, event):
        self._update_bounds()
        # keep dot inside bounds if resize made it outside
        x, y = self.dot.position()
        new_x = min(max(x, -self.max_x), self.max_x)
        new_y = min(max(y, -self.max_y), self.max_y)
        if new_x != x or new_y != y:
            self.dot.setposition(new_x, new_y)
        self.screen.update()

    # ----- movement helpers -----
    def _pick_new_direction_and_distance(self):
        angle = random.uniform(0, 360)
        distance = random.uniform(MIN_DISTANCE, MAX_DISTANCE)
        return angle, distance

    def _start_new_movement(self, angle_deg, distance, redirecting=False):
        self.state["target_angle"] = angle_deg % 360
        self.state["remaining_distance"] = float(distance)
        self.state["paused_until"] = time.time() + PAUSE_ON_TURN
        self.state["is_redirecting"] = bool(redirecting)

    def _schedule_redirect_to_center(self, push_distance=REDIRECT_STEP):
        x, y = self.dot.position()
        angle_to_center = self.dot.towards(0, 0)
        if abs(x) < 1 and abs(y) < 1:
            a, d = self._pick_new_direction_and_distance()
            self._start_new_movement(a, d, redirecting=False)
        else:
            self._start_new_movement(angle_to_center, push_distance, redirecting=True)

    # ----- animation loop (non-blocking) -----
    def frame_step(self):
        now = time.time()

        if not self.state["running"]:
            # not running -> still update display occasionally
            self.screen.update()
            return

        if now < self.state["paused_until"]:
            self.screen.update()
            # schedule next frame
            self.screen.ontimer(self.frame_step, self.state["frame_delay_ms"])
            return

        if self.state["target_angle"] is None or self.state["remaining_distance"] <= 0:
            a, d = self._pick_new_direction_and_distance()
            self._start_new_movement(a, d)
            self.screen.update()
            self.screen.ontimer(self.frame_step, self.state["frame_delay_ms"])
            return

        step = min(self.state["step_size"], self.state["remaining_distance"])
        # move the dot smoothly
        self.dot.setheading(self.state["target_angle"])
        self.dot.forward(step)
        self.state["remaining_distance"] -= step

        x, y = self.dot.position()
        if abs(x) > self.max_x or abs(y) > self.max_y:
            self._schedule_redirect_to_center(push_distance=REDIRECT_STEP)

        self.screen.update()
        self.screen.ontimer(self.frame_step, self.state["frame_delay_ms"])

    # ----- controls UI -----
    def _build_controls(self):
        # Start / Stop / Reset / Fullscreen
        start_btn = tk.Button(self.right_frame, text="Start", width=14, command=self.start)
        stop_btn = tk.Button(self.right_frame, text="Stop", width=14, command=self.stop)
        reset_btn = tk.Button(self.right_frame, text="Reset", width=14, command=self.reset_to_center)
        fullscreen_btn = tk.Button(self.right_frame, text="Toggle Fullscreen", width=14, command=self.toggle_fullscreen)

        start_btn.pack(pady=(4, 2))
        stop_btn.pack(pady=2)
        reset_btn.pack(pady=2)
        fullscreen_btn.pack(pady=(2, 10))

        # Speed slider
        tk.Label(self.right_frame, text="Speed").pack(anchor="w")
        self.speed_var = tk.DoubleVar(value=self.state["step_size"])
        speed_slider = tk.Scale(self.right_frame, from_=0.5, to=20.0, orient=tk.HORIZONTAL, resolution=0.5,
                                variable=self.speed_var, command=self._on_speed_change, length=220)
        speed_slider.pack(pady=(0, 8))

        # Dot size slider
        tk.Label(self.right_frame, text="Dot size").pack(anchor="w")
        self.size_var = tk.DoubleVar(value=1.0)
        size_slider = tk.Scale(self.right_frame, from_=0.5, to=6.0, orient=tk.HORIZONTAL, resolution=0.1,
                               variable=self.size_var, command=self._on_size_change, length=220)
        size_slider.set(1.0)
        size_slider.pack(pady=(0, 8))

        # Color chooser
        tk.Label(self.right_frame, text="Dot color").pack(anchor="w")
        color_btn = tk.Button(self.right_frame, text="Choose Color", command=self._choose_color)
        color_btn.pack(pady=(0, 8))

        # Pause on turn slider
        tk.Label(self.right_frame, text="Pause on turn (ms)").pack(anchor="w")
        self.pause_var = tk.IntVar(value=int(PAUSE_ON_TURN * 1000))
        pause_slider = tk.Scale(self.right_frame, from_=0, to=1000, orient=tk.HORIZONTAL,
                                variable=self.pause_var, command=self._on_pause_change, length=220)
        pause_slider.pack(pady=(0, 8))

        # Mode placeholder
        tk.Label(self.right_frame, text="Mode").pack(anchor="w")
        mode_var = tk.StringVar(value="Random")
        mode_menu = tk.OptionMenu(self.right_frame, mode_var, "Random", "Bounce (todo)", "Smooth-turn (todo)")
        mode_menu.config(width=20)
        mode_menu.pack(pady=(0, 8))

        # Info / spacing
        info = tk.Label(self.right_frame, text="Controls: Start/Stop, Reset, Fullscreen.\nAdjust speed, size, color, and pause.",
                        justify=tk.LEFT, wraplength=220)
        info.pack(side=tk.BOTTOM, pady=(12, 6))

    # ----- control callbacks -----
    def start(self):
        if not self.state["running"]:
            self.state["running"] = True
            # ensure there's a movement target
            if self.state["target_angle"] is None or self.state["remaining_distance"] <= 0:
                a, d = self._pick_new_direction_and_distance()
                self._start_new_movement(a, d)
            # start the ontimer loop
            self.screen.ontimer(self.frame_step, self.state["frame_delay_ms"])

    def stop(self):
        self.state["running"] = False

    def reset_to_center(self):
        self.dot.setposition(0, 0)
        self.state["target_angle"] = None
        self.state["remaining_distance"] = 0.0
        self.state["paused_until"] = 0.0
        self.state["is_redirecting"] = False
        self.screen.update()

    def toggle_fullscreen(self):
        # Works on Windows and Linux; macOS may behave differently
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)

    def _on_speed_change(self, val):
        try:
            v = float(val)
            self.state["step_size"] = v
        except Exception:
            pass

    def _on_size_change(self, val):
        try:
            v = float(val)
            # turtle shapesize scales the turtle shape; shape size 1 is baseline
            self.dot.shapesize(v, v, 1)
            self.screen.update()
        except Exception:
            pass

    def _choose_color(self):
        color = colorchooser.askcolor(title="Choose dot color", initialcolor=DOT_COLOR)
        if color and color[1]:
            hexcol = color[1]
            self.dot.color(hexcol)
            self.screen.update()

    def _on_pause_change(self, val):
        try:
            ms = int(val)
            self.state["paused_until"] = time.time()  # clear any existing pause
            # set future pauses to given value in seconds
            global PAUSE_ON_TURN
            PAUSE_ON_TURN = ms / 1000.0
        except Exception:
            pass

# ---------- main ----------
def main():
    root = tk.Tk()
    app = RandomDotApp(root)
    # Start maximized / zoomed by default (cross-platform attempts)
    try:
        root.state("zoomed")  # Windows
    except Exception:
        try:
            root.attributes("-zoomed", True)  # some Linux
        except Exception:
            # fallback: set the window to near-screen size
            root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

    # Start the turtle idle update loop so the canvas draws immediately
    app.screen.update()
    root.mainloop()

if __name__ == "__main__":
    main()
