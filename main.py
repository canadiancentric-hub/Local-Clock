# Copyright (c) 2026 Jeremy
# Licensed under the MIT License
import sys
import os
import tkinter as tk
from tkinter import ttk
from functools import partial
from datetime import datetime
from settings_manager import SettingsManager
from clock_logic import ClockLogic

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    os.environ['TCL_LIBRARY'] = os.path.join(bundle_dir, 'tcl')
    os.environ['TK_LIBRARY'] = os.path.join(bundle_dir, 'tk')

class LocalClockApp:
    def __init__(self):
        self.settings = SettingsManager()
        self.logic = ClockLogic(self.settings.get("time_offset"))
        
        self.root = tk.Tk()
        self.root.title("Local Clock")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.configure(bg=self.settings.get("bg_mode"))
        self.root.attributes("-alpha", self.settings.get("opacity"))

        self.settings_window = None
        self.is_fullscreen = False

        self.main_frame = tk.Frame(self.root, bg=self.settings.get("bg_mode"))
        self.main_frame.pack(expand=True, fill='both')

        self.label = tk.Label(self.main_frame, text="", font=('Ubuntu', 65, 'bold'), 
                             bg=self.settings.get("bg_mode"), fg=self.settings.get("current_color"))
        self.label.pack(expand=True)

        self.date_label = tk.Label(self.main_frame, text="", font=('Ubuntu', 18), 
                                  bg=self.settings.get("bg_mode"), fg=self.settings.get("current_color"))
        
        if self.settings.get("show_date"):
            self.date_label.pack(expand=True, pady=(0, 10))

        btn_config = {
            "bg": self.settings.get("bg_mode"), 
            "fg": "#555555", 
            "bd": 0, 
            "highlightthickness": 0,
            "activebackground": self.settings.get("bg_mode"),
            "activeforeground": "#777777"
        }

        self.close_btn = tk.Button(self.root, text="×", command=self.root.destroy, 
                                 font=("Arial", 14, "bold"), **btn_config)
        self.close_btn.place(x=15, y=10)

        self.min_btn = tk.Button(self.root, text="_", command=self.toggle_size, 
                                font=("Arial", 14, "bold"), 
                                bg=self.settings.get("bg_mode"), 
                                fg=self.settings.get("current_color"),
                                bd=0, highlightthickness=0)
        
        # Settings button - relocated to top right
        self.settings_btn = tk.Button(self.root, text="⋮", command=self.toggle_settings_ui, 
                                    font=("Arial", 18, "bold"), **btn_config)
        
        # Resize grip widget
        self.grip = ttk.Sizegrip(self.root)

        for widget in [self.main_frame, self.label, self.date_label]:
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.on_move)
            widget.bind("<Double-Button-1>", self.toggle_size)

        # Trigger rescaling when the window is manually resized
        self.root.bind("<Configure>", self.rescale_text)
        
        self.root.bind('<F11>', lambda e: self.toggle_size())
        self.root.bind('<Control-q>', lambda e: self.root.destroy())

        self.root.geometry("400x180+100+100")
        self.reposition_buttons()
        self.update_loop()
        self.root.mainloop()

    def rescale_text(self, event=None):
        """Calculates font size based on current window height during manual resize."""
        if not self.is_fullscreen:
            # We use height as the primary scaler to maintain vertical proportions
            h = self.root.winfo_height()
            main_fs = max(10, int(h * 65 / 180))
            date_fs = max(6, int(h * 18 / 180))
            self.label.config(font=('Ubuntu', main_fs, 'bold'))
            self.date_label.config(font=('Ubuntu', date_fs, ''))
            self.reposition_buttons()

    def update_loop(self):
        self.logic.tick()
        if datetime.now().minute == 0 and datetime.now().second == 0:
            if self.logic.check_clock_drift():
                self.settings.set("time_offset", 0)

        ts, ds = self.logic.get_time_data(self.settings.get("use_24h"))
        self.label.config(text=ts)
        self.date_label.config(text=ds)
        self.root.after(1000, self.update_loop)

    def start_move(self, event):
        self.x, self.y = event.x, event.y

    def on_move(self, event):
        if not self.is_fullscreen:
            x = self.root.winfo_x() + (event.x - self.x)
            y = self.root.winfo_y() + (event.y - self.y)
            self.root.geometry(f"+{x}+{y}")

    def toggle_size(self, event=None):
        if not self.is_fullscreen:
            self.previous_geometry = self.root.geometry()
            win_x = self.root.winfo_x()
            actual_sh = self.root.winfo_toplevel().winfo_screenheight()
            actual_sw = self.root.winfo_toplevel().winfo_screenwidth()
            actual_mon_w = actual_sw // 2 if actual_sw > 3000 else actual_sw
            monitor_offset = (win_x // actual_mon_w) * actual_mon_w
            self.root.geometry(f"{actual_mon_w}x{actual_sh}+{monitor_offset}+0")
            
            scaled_font = int(actual_sh * 350 / 1080)
            scaled_date = int(actual_sh * 72 / 1080)
            self.label.config(font=('Ubuntu', scaled_font, 'bold'))
            self.date_label.config(font=('Ubuntu', scaled_date, ''))
            self.is_fullscreen = True
            self.grip.place_forget()
        else:
            if hasattr(self, 'previous_geometry'):
                self.root.geometry(self.previous_geometry)
            else:
                self.root.geometry("400x180+100+100")
            
            self.is_fullscreen = False
            self.rescale_text() # Re-apply scaling for windowed mode
            
        self.reposition_buttons()

    def reposition_buttons(self):
        self.root.update_idletasks()
        curr_w = self.root.winfo_width()
        curr_h = self.root.winfo_height()
        
        # Settings now stays at the top right
        self.settings_btn.place(x=curr_w - 45, y=10)
        
        if self.is_fullscreen:
            self.min_btn.place(x=45, y=10)
            self.grip.place_forget()
        else:
            self.min_btn.place_forget()
            # Grip sits at the bottom right corner
            self.grip.place(x=curr_w - 15, y=curr_h - 15)

    def apply_color(self, col):
        self.settings.set("current_color", col)
        self.label.config(fg=col)
        self.date_label.config(fg=col)
        self.min_btn.config(fg=col)

    def toggle_theme(self):
        new_bg = "white" if self.settings.get("bg_mode") == "black" else "black"
        self.settings.set("bg_mode", new_bg)
        
        curr_col = self.settings.get("current_color").lower()
        
        if new_bg == "white" and (curr_col == "#ffffff" or curr_col == "white" or curr_col == "#ecf0f1"):
            self.apply_color("#000000")
        elif new_bg == "black" and (curr_col == "#000000" or curr_col == "black"):
            self.apply_color("#ffffff")
            
        self.root.configure(bg=new_bg)
        self.main_frame.configure(bg=new_bg)
        self.label.configure(bg=new_bg)
        self.date_label.configure(bg=new_bg)
        self.close_btn.configure(bg=new_bg, activebackground=new_bg)
        self.min_btn.configure(bg=new_bg, activebackground=new_bg)
        self.settings_btn.configure(bg=new_bg, activebackground=new_bg)
        
        if self.settings_window:
            self.toggle_settings_ui()
            self.toggle_settings_ui()

    def toggle_settings_ui(self):
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
            return
            
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.overrideredirect(True)
        self.settings_window.configure(bg='#222222', padx=15, pady=15)
        self.settings_window.wm_attributes("-topmost", True)
        
        menu_w, menu_h = 280, 530
        cx, cy = self.root.winfo_x(), self.root.winfo_y()
        cw, ch = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        actual_mon_w = sw if sw < 3000 else sw // 2 
        monitor_right = ((cx // actual_mon_w) * actual_mon_w) + actual_mon_w

        target_y = max(10, min(cy + (ch // 2) - (menu_h // 2), sh - menu_h - 10))
        target_x = monitor_right - menu_w - 20 if self.is_fullscreen else (cx + cw + 10 if cx + cw + 10 + menu_w <= monitor_right else cx - menu_w - 10)
        self.settings_window.geometry(f"{menu_w}x{menu_h}+{target_x}+{target_y}")

        tk.Label(self.settings_window, text="TRANSPARENCY", bg="#222222", fg="#888888", font=("Arial", 8, "bold")).pack()
        ttk.Scale(self.settings_window, from_=0.2, to=1.0, value=self.settings.get("opacity"), 
                  command=lambda v: [self.root.attributes("-alpha", float(v)), self.settings.set("opacity", float(v))]).pack(fill="x", padx=20, pady=5)

        tk.Label(self.settings_window, text="ADJUST TIME", bg="#222222", fg="#888888", font=("Arial", 8, "bold"), pady=5).pack()
        tf = tk.Frame(self.settings_window, bg="#222222")
        tf.pack()
        btn_style = {"bg": "#333333", "fg": "white", "bd": 0, "width": 5, "pady": 5}
        
        for i, (txt, sec) in enumerate([("+1H", 3600), ("-1H", -3600), ("+1M", 60), ("-1M", -60)]):
            cmd = lambda s=sec: self.settings.set("time_offset", self.logic.adjust_time(s))
            tk.Button(tf, text=txt, command=cmd, **btn_style).grid(row=i//2, column=i%2, padx=2, pady=2)

        tk.Button(self.settings_window, text="RESYNC TO COMPUTER", 
                  command=lambda: self.settings.set("time_offset", self.logic.reset_offset()), 
                  bg="#444444", fg="#2ecc71", bd=0, font=("Arial", 8, "bold"), pady=10).pack(fill="x", pady=10)
        
        tk.Button(self.settings_window, text="LIGHT / DARK MODE", command=self.toggle_theme, bg="#333333", fg="white", bd=0, pady=5).pack(fill="x", pady=2)
        
        tk.Button(self.settings_window, text="12H / 24H TOGGLE", 
                  command=lambda: self.settings.set("use_24h", not self.settings.get("use_24h")), 
                  bg="#333333", fg="white", bd=0, pady=5).pack(fill="x", pady=2)
        
        def toggle_date():
            show = not self.settings.get("show_date")
            self.settings.set("show_date", show)
            if show:
                self.date_label.pack(expand=True, pady=(0, 10))
            else:
                self.date_label.pack_forget()

        tk.Button(self.settings_window, text="SHOW / HIDE DATE", command=toggle_date, bg="#333333", fg="white", bd=0, pady=5).pack(fill="x", pady=2)
        
        fc = tk.Frame(self.settings_window, bg="#222222")
        fc.pack(pady=10)
        contrast = "#000000" if self.settings.get("bg_mode") == "white" else "#ffffff"
        clrs = ["#2ecc71", "#3498db", "#e74c3c", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22", contrast]
        for i, c in enumerate(clrs):
            tk.Button(fc, bg=c, width=4, height=1, bd=0, command=partial(self.apply_color, c)).grid(row=i//4, column=i%4, padx=4, pady=4)

        tk.Button(self.settings_window, text="CLOSE SETTINGS", command=self.settings_window.destroy, bg="#c0392b", fg="white", bd=0, pady=10).pack(fill="x", pady=5)

if __name__ == "__main__":
    LocalClockApp()
