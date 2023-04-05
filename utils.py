from flask import Response
from queue import Queue


progress_queue = Queue()

def send_progress():
    def generate():
        while True:
            progress_num = progress_queue.get()
            if progress_num is None:
                break
            yield 'data: %d\n\n' % progress_num
    return Response(generate(), mimetype='text/event-stream')