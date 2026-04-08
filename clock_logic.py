# Copyright (c) 2026 Jeremy
# Licensed under the MIT License
import time
from datetime import datetime

class ClockLogic:
    def __init__(self, initial_offset=0):
        self.time_offset = initial_offset
        self.total_seconds = 0
        self.sync_to_system()

    def sync_to_system(self):
        """Synchronizes the internal counter with the system clock plus the user offset."""
        now = datetime.now()
        sys_secs = (now.hour * 3600) + (now.minute * 60) + now.second
        self.total_seconds = (sys_secs + self.time_offset) % 86400

    def tick(self):
        """Increments time and performs a hard sync every minute to prevent software lag."""
        self.total_seconds = (self.total_seconds + 1) % 86400
        # Re-sync every minute to prevent drift
        if datetime.now().second == 0:
            self.sync_to_system()

    def adjust_time(self, seconds):
        """Adjusts the user-defined offset and resyncs immediately."""
        self.time_offset += seconds
        self.sync_to_system()
        return self.time_offset

    def reset_offset(self):
        """Clears all user offsets to match system time exactly."""
        self.time_offset = 0
        self.sync_to_system()
        return 0

    def get_time_data(self, use_24h):
        """Formats the internal time into strings for the UI display."""
        h = (self.total_seconds // 3600) % 24
        m = (self.total_seconds // 60) % 60
        s = self.total_seconds % 60
        
        if use_24h:
            ts = f"{h:02}:{m:02}:{s:02}"
        else:
            hr = 12 if h % 12 == 0 else h % 12
            ts = f"{hr}:{m:02}:{s:02}"
        
        date_str = datetime.now().strftime("%A, %b %d, %Y")
        return ts, date_str

    def check_clock_drift(self):
        """Resets offset if internal time drifts more than 5 minutes from system."""
        # Fix: Added missing 'import time' at top of file to allow time.time()
        now = datetime.now()
        expected = time.time()
        # If the difference is > 300 seconds (5 mins), reset
        if abs((now.timestamp() - expected)) > 300:
            self.reset_offset()
            return True # Signal that a reset happened
        return False
