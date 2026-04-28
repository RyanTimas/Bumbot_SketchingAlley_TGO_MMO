import os
from datetime import datetime

from src.resources.constants.file_paths import LOGS_DIR


class LogHandler:
    def __init__(self, logfile_name: str, use_military_time: bool = True):
        self.logfile_name = logfile_name
        self.date_format = "%H:%M:%S" if use_military_time else "%I:%M:%S %p"

        filename_format = "%Y-%m-%d_%H-%M-%S" if use_military_time else "%Y-%m-%d_%I-%M-%S_%p"
        current_time = datetime.now().strftime(filename_format)
        log_filename = f"{logfile_name}_{current_time}.log"
        self.log_path = os.path.join(LOGS_DIR, log_filename)
        self.log_file = None

    def __enter__(self):
        self.log_file = open(self.log_path, 'w', encoding='utf-8')

        self.log_file.write(f"{self.logfile_name} Log - {datetime.now().strftime(f'%m/%d/%Y {self.date_format}')}\n")
        self.log_file.write("=" * 80 + "\n\n")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.log_file:
            self.log_file.close()

    def write(self, message: str,):
        if self.log_file:
            timestamp = datetime.now().strftime(self.date_format)
            self.log_file.write(f"[{timestamp}] {message}")
            self.log_file.flush()