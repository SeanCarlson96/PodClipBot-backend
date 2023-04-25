from proglog import ProgressBarLogger
from math import floor

class MyBarLogger(ProgressBarLogger):
    def __init__(self, socketio):
        super().__init__(init_state=None, bars=None, ignored_bars=None,
                 logged_bars='all', min_time_interval=0, ignore_bars_under=0)
        self.socketio = socketio

    def callback(self, **changes):
        try:
            index = self.state['bars']['t']['index']
            total = self.state['bars']['t']['total']
            percent_complete = index / total * 100
            if percent_complete < 0:
                percent_complete = 0
            if percent_complete > 100:
                percent_complete = 100
            self.socketio.emit('video_processing_progress', {'progress': percent_complete})
        except KeyError as e:
            pass
