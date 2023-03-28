from flask import Flask, request, render_template
from edit_video import edit_video

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trim', methods=['POST'])
def trim_video():
    # Get the form data from the request
    video_file = request.files.get('video-file')
    start_time = float(request.form.get('start-time'))
    end_time = float(request.form.get('end-time'))

    return edit_video(video_file, start_time, end_time)

if __name__ == '__main__':
    app.run()