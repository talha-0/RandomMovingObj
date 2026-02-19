import tkinter as tk
import customtkinter as ctk
import turtle
import random
import time

BG_COLOR = "#2b2b2b" 
DOT_COLOR = "#1f6aa5"
STEP_SIZE = 3.0
FRAME_DELAY_MS = 16
PAUSE_ON_TURN = 0.35
MIN_DISTANCE = 100
MAX_DISTANCE = 600
EDGE_MARGIN = 15
REDIRECT_STEP = 150

class RandomDotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("blue") 

        self.title("Random Moving Dot")
        self.geometry("1000x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Left Frame: Canvas Container
        self.left_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Right Frame: Controls
        self.right_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.canvas_widget = tk.Canvas(self.left_frame, bg=BG_COLOR, highlightthickness=0)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.screen = turtle.TurtleScreen(self.canvas_widget)
        self.screen.bgcolor(BG_COLOR)
        self.screen.tracer(0)

        self.dot = turtle.RawTurtle(self.screen)
        self._configure_dot()

        self.max_x = 0
        self.max_y = 0
        self._update_bounds()

        self.anim_state = {
            "target_angle": None,
            "remaining_distance": 0.0,
            "paused_until": 0.0,
            "is_redirecting": False,
            "running": False,
            "step_size": STEP_SIZE,
            "frame_delay_ms": FRAME_DELAY_MS
        }
        self._build_controls()

        self.canvas_widget.bind("<Configure>", self._on_canvas_configure)

        a, d = self._pick_new_direction_and_distance()
        self._start_new_movement(a, d)

    def _configure_dot(self):
        self.dot.hideturtle()
        self.dot.shape("circle")
        self.dot.shapesize(1)
        self.dot.color(DOT_COLOR)
        self.dot.penup()
        self.dot.speed(0)
        self.dot.showturtle()

    def _update_bounds(self):
        width = max(self.canvas_widget.winfo_width(), 1)
        height = max(self.canvas_widget.winfo_height(), 1)
        self.max_x = width / 2.0 - EDGE_MARGIN
        self.max_y = height / 2.0 - EDGE_MARGIN

    def _on_canvas_configure(self, event):
        self._update_bounds()
        x, y = self.dot.position()
        new_x = min(max(x, -self.max_x), self.max_x)
        new_y = min(max(y, -self.max_y), self.max_y)
        if new_x != x or new_y != y:
            self.dot.setposition(new_x, new_y)
        self.screen.update()

    def _pick_new_direction_and_distance(self):
        angle = random.uniform(0, 360)
        distance = random.uniform(MIN_DISTANCE, MAX_DISTANCE)
        return angle, distance

    def _start_new_movement(self, angle_deg, distance, redirecting=False):
        self.anim_state["target_angle"] = angle_deg % 360
        self.anim_state["remaining_distance"] = float(distance)
        self.anim_state["paused_until"] = time.time() + PAUSE_ON_TURN
        self.anim_state["is_redirecting"] = bool(redirecting)

    def _schedule_redirect_to_center(self, push_distance=REDIRECT_STEP):
        x, y = self.dot.position()
        angle_to_center = self.dot.towards(0, 0)
        if abs(x) < 1 and abs(y) < 1:
            a, d = self._pick_new_direction_and_distance()
            self._start_new_movement(a, d, redirecting=False)
        else:
            self._start_new_movement(angle_to_center, push_distance, redirecting=True)

    def frame_step(self):
        now = time.time()

        if not self.anim_state["running"]:
            self.screen.update()
            return

        if now < self.anim_state["paused_until"]:
            self.screen.update()
            self.screen.ontimer(self.frame_step, self.anim_state["frame_delay_ms"])
            return

        if self.anim_state["target_angle"] is None or self.anim_state["remaining_distance"] <= 0:
            a, d = self._pick_new_direction_and_distance()
            self._start_new_movement(a, d)
            self.screen.update()
            self.screen.ontimer(self.frame_step, self.anim_state["frame_delay_ms"])
            return

        step = min(self.anim_state["step_size"], self.anim_state["remaining_distance"])
        self.dot.setheading(self.anim_state["target_angle"])
        self.dot.forward(step)
        self.anim_state["remaining_distance"] -= step

        x, y = self.dot.position()
        if abs(x) > self.max_x or abs(y) > self.max_y:
            self._schedule_redirect_to_center(push_distance=REDIRECT_STEP)

        self.screen.update()
        self.screen.ontimer(self.frame_step, self.anim_state["frame_delay_ms"])

    def _build_controls(self):
        title_lbl = ctk.CTkLabel(self.right_frame, text="Controls", font=("Roboto", 20, "bold"))
        title_lbl.pack(pady=(20, 15), padx=20, anchor="w")

        # Buttons with rounded corners and hover effects
        self.start_btn = ctk.CTkButton(self.right_frame, text="Start Animation", command=self.start, fg_color="#2CC985")
        self.start_btn.pack(pady=5, padx=20, fill="x")

        self.stop_btn = ctk.CTkButton(self.right_frame, text="Stop", command=self.stop, fg_color="#C92C2C")
        self.stop_btn.pack(pady=5, padx=20, fill="x")

        self.reset_btn = ctk.CTkButton(self.right_frame, text="Reset Position", command=self.reset_to_center, fg_color="transparent", border_width=2)
        self.reset_btn.pack(pady=5, padx=20, fill="x")

        # Separator
        ctk.CTkLabel(self.right_frame, text="Settings", font=("Roboto", 16)).pack(pady=(20, 10), padx=20, anchor="w")

        # Speed Slider
        ctk.CTkLabel(self.right_frame, text="Speed").pack(padx=20, anchor="w")
        self.speed_slider = ctk.CTkSlider(self.right_frame, from_=0.5, to=20.0, command=self._on_speed_change)
        self.speed_slider.set(self.anim_state["step_size"])
        self.speed_slider.pack(pady=(0, 15), padx=20, fill="x")

        # Dot Size Slider
        ctk.CTkLabel(self.right_frame, text="Dot Size").pack(padx=20, anchor="w")
        self.size_slider = ctk.CTkSlider(self.right_frame, from_=0.5, to=6.0, command=self._on_size_change)
        self.size_slider.set(1.0)
        self.size_slider.pack(pady=(0, 15), padx=20, fill="x")

        # Pause Slider
        ctk.CTkLabel(self.right_frame, text="Pause Duration").pack(padx=20, anchor="w")
        self.pause_slider = ctk.CTkSlider(self.right_frame, from_=0, to=1000, command=self._on_pause_change)
        self.pause_slider.set(int(PAUSE_ON_TURN * 1000))
        self.pause_slider.pack(pady=(0, 15), padx=20, fill="x")

        # Color Option
        ctk.CTkLabel(self.right_frame, text="Color Theme").pack(padx=20, anchor="w")
        self.color_option = ctk.CTkOptionMenu(self.right_frame, values=["Cyan", "Red", "Green", "Yellow", "White"],
                                              command=self._on_color_preset)
        self.color_option.pack(pady=(0, 20), padx=20, fill="x")

    def start(self):
        if not self.anim_state["running"]:
            self.anim_state["running"] = True
            if self.anim_state["target_angle"] is None or self.anim_state["remaining_distance"] <= 0:
                a, d = self._pick_new_direction_and_distance()
                self._start_new_movement(a, d)
            self.screen.ontimer(self.frame_step, self.anim_state["frame_delay_ms"])

    def stop(self):
        self.anim_state["running"] = False

    def reset_to_center(self):
        self.dot.setposition(0, 0)
        self.anim_state["target_angle"] = None
        self.anim_state["remaining_distance"] = 0.0
        self.anim_state["paused_until"] = 0.0
        self.anim_state["is_redirecting"] = False
        self.screen.update()

    def _on_speed_change(self, val):
        self.anim_state["step_size"] = float(val)

    def _on_size_change(self, val):
        v = float(val)
        self.dot.shapesize(v, v, 1)
        self.screen.update()

    def _on_pause_change(self, val):
        global PAUSE_ON_TURN
        PAUSE_ON_TURN = float(val) / 1000.0
        self.anim_state["paused_until"] = time.time()

    def _on_color_preset(self, choice):
        # Map simple presets to hex for the turtle
        colors = {"Cyan": "cyan", "Red": "#ff5555", "Green": "#50fa7b", "Yellow": "#f1fa8c", "White": "white"}
        self.dot.color(colors.get(choice, "cyan"))
        self.screen.update()

if __name__ == "__main__":
    app = RandomDotApp()
    app.mainloop()