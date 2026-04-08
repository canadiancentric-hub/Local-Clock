# Copyright (c) 2026 Jeremy
# Licensed under the MIT License
import json
import os
import shutil
import logging
import threading

logging.basicConfig(filename="local_clock.log", level=logging.INFO)
logger = logging.getLogger(__name__)

class SettingsManager:
    def __init__(self):
        self.state_file = os.path.join(os.path.expanduser("~"), ".local_clock_state.json")
        self.data = self._load_state()
        self._save_timer = None

    def _load_state(self):
        if not os.path.exists(self.state_file):
            return self.get_default_data()
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.error(f"Failed to load state: {e}")
            return self.get_default_data()

    def get_default_data(self):
        """Initializes default settings for the clock."""
        return {
            "time_offset": 0, 
            "current_color": "#ffffff", # Default to White
            "show_date": False,
            "bg_mode": "black",         # Default to Black
            "opacity": 1.0, 
            "use_24h": False
        }

    def force_save(self):
        """Immediately writes to disk and cancels any pending timers."""
        if self._save_timer:
            self._save_timer.cancel()
        self.save_to_disk()

    def save_to_disk(self):
        """Handles the physical writing of the JSON state file."""
        try:
            # Create a backup before overwriting
            if os.path.exists(self.state_file):
                shutil.copy(self.state_file, self.state_file + ".bak")
            with open(self.state_file, "w") as f:
                json.dump(self.data, f, indent=2)
            logger.info("State saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.schedule_save()

    def schedule_save(self):
        """Batches save requests to prevent excessive disk I/O."""
        if self._save_timer:
            self._save_timer.cancel()
        # Reduced to 1.0 second for more responsive memory
        self._save_timer = threading.Timer(1.0, self.save_to_disk)
        self._save_timer.start()
