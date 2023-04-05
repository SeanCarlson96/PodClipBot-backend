import re
import logging

class ProgressLogger(logging.Logger):
    def __init__(self, name, app):
        super().__init__(name)
        self.app = app

    def debug(self, msg, *args, **kwargs):
        progress_match = re.search(r'\d+\.\d+%', msg)
        if progress_match:
            progress_value = float(progress_match.group()[:-1])
            with self.app.app_context():
                self.app.progress_value = progress_value
                print(f"data: {progress_value}\n\n")
        super().debug(msg, *args, **kwargs)
