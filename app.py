from flask import Flask, request, send_from_directory
from flask_cors import CORS
from edit_video import edit_video

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

@app.route('/trim', methods=['POST'])
def trim_video():
    # # Get the form data from the request
    # video_file = request.files.get('video-file')
    # start_time = float(request.form.get('start-time'))
    # end_time = float(request.form.get('end-time'))

    # return edit_video(video_file, start_time, end_time)

    # Get the form data from the request
    video_file = request.files.get('video-file')
    start_time = float(request.form.get('start-time'))
    end_time = float(request.form.get('end-time'))

    # Save the edited video file to a specific directory, e.g., 'uploads'
    output_filename = edit_video(video_file, start_time, end_time)
    return send_from_directory('uploads', output_filename)

if __name__ == '__main__':
    app.run()