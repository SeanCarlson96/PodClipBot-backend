from proglog import ProgressBarLogger
from tqdm import tqdm
class CancelProcessingException(Exception):
    def __init__(self, message):
        super().__init__(message)
class MyBarLogger(ProgressBarLogger):
    def __init__(self, socketio, clip_cancel_flags, clip_name, socket_id):
        super().__init__(
            init_state=None,
            bars=None,
            ignored_bars=None,
            logged_bars="all",
            min_time_interval=0,
            ignore_bars_under=0,
        )
        self.socketio = socketio
        self.clip_cancel_flags = clip_cancel_flags
        self.clip_name = clip_name
        self.progress_bar = None
        self.socket_id = socket_id


    def callback(self, **changes):
        try:
            index = self.state["bars"]["t"]["index"]
            total = self.state["bars"]["t"]["total"]
            percent_complete = index / total * 100
            if percent_complete < 0:
                percent_complete = 0
            if percent_complete > 100:
                percent_complete = 100

            if self.progress_bar is None:
                self.progress_bar = tqdm(total=total, unit="frame", desc=self.clip_name)

            self.progress_bar.update(index - self.progress_bar.n)

            adjusted_percent_complete = percent_complete / 1.42857142857 + 30

            # self.socketio.emit("video_processing_progress", {"progress": percent_complete})
            self.socketio.emit("video_processing_progress", {"progress": adjusted_percent_complete}, room=self.socket_id)
        except KeyError as e:
            pass

        # Check if the cancel flag for this clip_name is set to True
        if self.clip_cancel_flags.get(self.clip_name, False):
            if self.progress_bar is not None:
                self.progress_bar.update(total - self.progress_bar.n)
                self.progress_bar.close()
            self.socketio.emit("video_processing_progress", {"progress": 0}, room=self.socket_id)
            raise CancelProcessingException(
                f"{self.clip_name} processing was canceled during logger."
            )
