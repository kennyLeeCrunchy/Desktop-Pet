from __future__ import annotations

import ctypes
import json
import os
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageTk


APP_NAME = "GALGYO"
APP_VERSION = "1.0.0"
FRAME_WIDTH = 192
FRAME_HEIGHT = 208
TRANSPARENT_COLOR = "#010203"
ERROR_ALREADY_EXISTS = 183


@dataclass(frozen=True)
class Animation:
    row: int
    frames: int
    interval_ms: int
    label: str


ANIMATIONS = {
    "idle": Animation(0, 6, 180, "Blinking"),
    "running-right": Animation(1, 8, 105, "Dragging Right"),
    "running-left": Animation(2, 8, 105, "Dragging Left"),
    "waving": Animation(3, 4, 180, "Waving"),
    "jumping": Animation(4, 5, 135, "Jumping"),
    "failed": Animation(5, 8, 170, "Feeling Sad"),
    "waiting": Animation(6, 6, 190, "Asking"),
    "working": Animation(7, 6, 145, "Thinking"),
    "review": Animation(8, 6, 165, "Sitting"),
}

MIN_SCALE = 0.5
MAX_SCALE = 2.0

MENU_STATES = (
    "idle",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "working",
    "review",
)

HOVER_OPTIONS = (
    ("Disabled", "none"),
    ("Blinking", "idle"),
    ("Waving", "waving"),
    ("Jumping", "jumping"),
    ("Feeling Sad", "failed"),
    ("Asking", "waiting"),
    ("Thinking", "working"),
    ("Sitting", "review"),
)


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def settings_path() -> Path:
    app_data = Path(os.environ.get("APPDATA", Path.home()))
    folder = app_data / "GalgyoDesktopPet"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"


def enable_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def enforce_single_instance() -> None:
    if sys.platform != "win32":
        return
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, "GALGYO.DesktopPet.Singleton")
    if not handle:
        return
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(
            None,
            "GALGYO is already running.",
            APP_NAME,
            0x40,
        )
        raise SystemExit(0)
    enforce_single_instance.handle = handle


class GalgyoPet:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.configure(bg=TRANSPARENT_COLOR)
        self.root.attributes("-transparentcolor", TRANSPARENT_COLOR)

        self.settings = self.load_settings()
        self.scale = min(
            MAX_SCALE,
            max(MIN_SCALE, float(self.settings.get("scale", 1.0))),
        )
        self.always_on_top = tk.BooleanVar(
            value=bool(self.settings.get("always_on_top", True))
        )
        self.lock_position = tk.BooleanVar(
            value=bool(self.settings.get("lock_position", False))
        )
        saved_mode = str(self.settings.get("mode", "idle"))
        if saved_mode not in MENU_STATES:
            saved_mode = "idle"
        self.mode = tk.StringVar(value=saved_mode)
        saved_hover_action = str(self.settings.get("hover_action", "waving"))
        valid_hover_actions = {value for _label, value in HOVER_OPTIONS}
        if saved_hover_action not in valid_hover_actions:
            saved_hover_action = "waving"
        self.hover_action = tk.StringVar(value=saved_hover_action)

        self.root.attributes("-topmost", self.always_on_top.get())
        self.atlas = Image.open(resource_path("assets/spritesheet.png")).convert("RGBA")
        self.frame_cache: dict[str, list[ImageTk.PhotoImage]] = {}
        self.display_width = 0
        self.display_height = 0
        self.rebuild_frames()

        self.canvas = tk.Canvas(
            self.root,
            width=self.display_width,
            height=self.display_height,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()
        self.image_item = self.canvas.create_image(0, 0, anchor="nw")

        self.animation_index = 0
        self.last_render_mode = ""
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.last_drag_root_x = 0
        self.is_dragging = False
        self.drag_direction: str | None = None
        self.hover_active = False
        self.temporary_mode: str | None = None
        self.wave_return_job: str | None = None
        self.resize_window: tk.Toplevel | None = None
        self.resize_job: str | None = None
        self.pending_scale = self.scale
        self.resize_value_text: tk.StringVar | None = None

        self.build_menu()
        self.bind_events()
        self.restore_position()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.tick()

    def load_settings(self) -> dict:
        try:
            return json.loads(settings_path().read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def save_settings(self) -> None:
        data = {
            "x": self.root.winfo_x(),
            "y": self.root.winfo_y(),
            "scale": self.scale,
            "mode": self.mode.get(),
            "hover_action": self.hover_action.get(),
            "always_on_top": self.always_on_top.get(),
            "lock_position": self.lock_position.get(),
        }
        try:
            settings_path().write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def restore_position(self) -> None:
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        default_x = max(0, screen_w - self.display_width - 48)
        default_y = max(0, screen_h - self.display_height - 80)
        x = int(self.settings.get("x", default_x))
        y = int(self.settings.get("y", default_y))
        x = min(max(0, x), max(0, screen_w - self.display_width))
        y = min(max(0, y), max(0, screen_h - self.display_height))
        self.root.geometry(
            f"{self.display_width}x{self.display_height}+{x}+{y}"
        )

    def rebuild_frames(self) -> None:
        self.display_width = max(1, round(FRAME_WIDTH * self.scale))
        self.display_height = max(1, round(FRAME_HEIGHT * self.scale))
        self.frame_cache.clear()

        for state, animation in ANIMATIONS.items():
            frames = []
            for column in range(animation.frames):
                frames.append(self.make_photo(animation.row, column))
            self.frame_cache[state] = frames

    def make_photo(self, row: int, column: int) -> ImageTk.PhotoImage:
        left = column * FRAME_WIDTH
        top = row * FRAME_HEIGHT
        frame = self.atlas.crop(
            (left, top, left + FRAME_WIDTH, top + FRAME_HEIGHT)
        )
        if frame.size != (self.display_width, self.display_height):
            frame = frame.resize(
                (self.display_width, self.display_height),
                Image.Resampling.LANCZOS,
            )
        return ImageTk.PhotoImage(frame)

    def build_menu(self) -> None:
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="Galgyo", state="disabled")
        self.menu.add_separator()

        for state in MENU_STATES:
            animation = ANIMATIONS[state]
            self.menu.add_radiobutton(
                label=animation.label,
                value=state,
                variable=self.mode,
                command=lambda selected=state: self.set_mode(selected),
            )

        self.menu.add_separator()
        hover_menu = tk.Menu(self.menu, tearoff=False)
        for label, state in HOVER_OPTIONS:
            hover_menu.add_radiobutton(
                label=label,
                value=state,
                variable=self.hover_action,
                command=self.set_hover_action,
            )
        self.menu.add_cascade(label="Hover Action", menu=hover_menu)
        self.menu.add_command(label="Resize...", command=self.open_resize_dialog)
        self.menu.add_checkbutton(
            label="Always on Top",
            variable=self.always_on_top,
            command=self.toggle_topmost,
        )
        self.menu.add_checkbutton(
            label="Lock Position",
            variable=self.lock_position,
            command=self.save_settings,
        )
        self.menu.add_separator()
        self.menu.add_command(label="About Galgyo", command=self.show_about)
        self.menu.add_command(label="Quit", command=self.quit)

    def bind_events(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.finish_drag)
        self.canvas.bind("<Double-Button-1>", self.wave_hello)
        self.canvas.bind("<Button-3>", self.show_menu)
        self.canvas.bind("<Enter>", self.start_hover)
        self.canvas.bind("<Leave>", self.finish_hover)

    def start_drag(self, event: tk.Event) -> None:
        if self.lock_position.get():
            return
        self.drag_offset_x = event.x_root - self.root.winfo_x()
        self.drag_offset_y = event.y_root - self.root.winfo_y()
        self.last_drag_root_x = event.x_root
        self.is_dragging = True
        self.drag_direction = None

    def drag(self, event: tk.Event) -> None:
        if self.lock_position.get():
            return
        delta_x = event.x_root - self.last_drag_root_x
        if delta_x > 1:
            direction = "running-right"
        elif delta_x < -1:
            direction = "running-left"
        else:
            direction = self.drag_direction
        if direction != self.drag_direction:
            self.drag_direction = direction
            self.animation_index = 0
        self.last_drag_root_x = event.x_root
        x = event.x_root - self.drag_offset_x
        y = event.y_root - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")

    def finish_drag(self, _event: tk.Event | None = None) -> None:
        if not self.is_dragging:
            return
        self.is_dragging = False
        self.drag_direction = None
        self.animation_index = 0
        self.save_settings()

    def start_hover(self, _event: tk.Event | None = None) -> None:
        self.hover_active = True
        self.animation_index = 0

    def finish_hover(self, _event: tk.Event | None = None) -> None:
        self.hover_active = False
        self.animation_index = 0

    def show_menu(self, event: tk.Event) -> None:
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def set_mode(self, mode: str) -> None:
        if mode not in MENU_STATES:
            mode = "idle"
        if self.wave_return_job:
            self.root.after_cancel(self.wave_return_job)
            self.wave_return_job = None
        self.temporary_mode = None
        self.mode.set(mode)
        self.animation_index = 0
        self.save_settings()

    def wave_hello(self, _event: tk.Event | None = None) -> None:
        if self.wave_return_job:
            self.root.after_cancel(self.wave_return_job)
        self.temporary_mode = "waving"
        self.animation_index = 0
        self.wave_return_job = self.root.after(2200, self.finish_wave)

    def finish_wave(self) -> None:
        self.temporary_mode = None
        self.wave_return_job = None
        self.animation_index = 0

    def set_hover_action(self) -> None:
        self.animation_index = 0
        self.save_settings()

    def open_resize_dialog(self) -> None:
        if self.resize_window and self.resize_window.winfo_exists():
            self.resize_window.lift()
            self.resize_window.focus_force()
            return

        window = tk.Toplevel(self.root)
        self.resize_window = window
        window.title("Resize Galgyo")
        window.resizable(False, False)
        window.attributes("-topmost", True)
        window.protocol("WM_DELETE_WINDOW", self.close_resize_dialog)

        self.resize_value_text = tk.StringVar(
            value=f"{round(self.scale * 100)}%"
        )
        tk.Label(
            window,
            text="Size",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        ).pack()
        tk.Label(
            window,
            textvariable=self.resize_value_text,
            font=("Segoe UI", 10),
        ).pack()

        slider = tk.Scale(
            window,
            from_=round(MIN_SCALE * 100),
            to=round(MAX_SCALE * 100),
            orient="horizontal",
            resolution=1,
            showvalue=False,
            length=300,
            command=self.queue_scale,
        )
        self.resize_slider = slider
        slider.set(round(self.scale * 100))
        slider.pack(padx=18, pady=(4, 10))
        slider.bind("<ButtonRelease-1>", self.apply_pending_scale)

        button_row = tk.Frame(window)
        button_row.pack(pady=(0, 12))
        tk.Button(
            button_row,
            text="100%",
            width=9,
            command=lambda: slider.set(100),
        ).pack(side="left", padx=4)
        tk.Button(
            button_row,
            text="Close",
            width=9,
            command=self.close_resize_dialog,
        ).pack(side="left", padx=4)

        window.update_idletasks()
        x = self.root.winfo_x() + self.display_width + 12
        y = self.root.winfo_y()
        x = min(x, self.root.winfo_screenwidth() - window.winfo_width() - 12)
        y = min(y, self.root.winfo_screenheight() - window.winfo_height() - 12)
        window.geometry(f"+{max(12, x)}+{max(12, y)}")

    def queue_scale(self, percent: str) -> None:
        self.pending_scale = min(
            MAX_SCALE,
            max(MIN_SCALE, float(percent) / 100.0),
        )
        if self.resize_value_text:
            self.resize_value_text.set(f"{round(self.pending_scale * 100)}%")
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(80, self.apply_pending_scale)

    def apply_pending_scale(self, _event: tk.Event | None = None) -> None:
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
            self.resize_job = None
        self.set_scale(self.pending_scale)

    def close_resize_dialog(self) -> None:
        self.apply_pending_scale()
        if self.resize_window and self.resize_window.winfo_exists():
            self.resize_window.destroy()
        self.resize_window = None

    def set_scale(self, scale: float) -> None:
        scale = min(MAX_SCALE, max(MIN_SCALE, round(float(scale), 2)))
        if abs(scale - self.scale) < 0.001:
            return
        old_x = self.root.winfo_x()
        old_y = self.root.winfo_y()
        self.scale = scale
        self.rebuild_frames()
        self.canvas.configure(
            width=self.display_width,
            height=self.display_height,
        )
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = min(max(0, old_x), max(0, screen_w - self.display_width))
        y = min(max(0, old_y), max(0, screen_h - self.display_height))
        self.root.geometry(f"{self.display_width}x{self.display_height}+{x}+{y}")
        self.animation_index = 0
        self.save_settings()

    def toggle_topmost(self) -> None:
        self.root.attributes("-topmost", self.always_on_top.get())
        self.save_settings()

    def show_about(self) -> None:
        messagebox.showinfo(
            APP_NAME,
            "Galgyo\n\n"
            "An unofficial fan-made character inspired by Winter.\n"
            "This project is non-commercial and is not affiliated with any rights holder.\n\n"
            "Left-drag: Move with directional running\n"
            "Double-click: Wave\n"
            "Right-click: Actions, hover behavior, and settings\n\n"
            f"Version {APP_VERSION}",
            parent=self.root,
        )

    def tick(self) -> None:
        mode = self.effective_mode()
        if mode != self.last_render_mode:
            self.animation_index = 0
            self.last_render_mode = mode
        animation = ANIMATIONS.get(mode, ANIMATIONS["idle"])
        frames = self.frame_cache.get(mode, self.frame_cache["idle"])
        frame = frames[self.animation_index % len(frames)]
        self.canvas.itemconfigure(self.image_item, image=frame)
        self.animation_index = (self.animation_index + 1) % len(frames)
        delay = animation.interval_ms

        self.root.after(delay, self.tick)

    def effective_mode(self) -> str:
        if self.is_dragging and self.drag_direction:
            return self.drag_direction
        if self.temporary_mode:
            return self.temporary_mode
        hover_mode = self.hover_action.get()
        if self.hover_active and hover_mode in MENU_STATES:
            return hover_mode
        return self.mode.get()

    def quit(self) -> None:
        self.save_settings()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    enable_dpi_awareness()
    enforce_single_instance()
    app = GalgyoPet()
    try:
        app.root.iconbitmap(resource_path("assets/galgyo.ico"))
    except tk.TclError:
        pass
    app.run()


if __name__ == "__main__":
    main()
