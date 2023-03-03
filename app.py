from flask import Flask, request, jsonify
from moviepy.video.io.VideoFileClip import VideoFileClip

app = Flask(__name__)

@app.route('/trim', methods=['POST'])
def trim_video():
    # Get the form data from the request
    file = request.files['video-file']
    start_time = float(request.form['start-time'])
    end_time = float(request.form['end-time'])

    # Save the video file to a temporary location
    temp_file = 'temp.mp4'
    file.save(temp_file)

    # Trim the video using MoviePy
    video = VideoFileClip(temp_file)
    trimmed_video = video.subclip(start_time, end_time)
    trimmed_file = 'trimmed.mp4'
    trimmed_video.write_videofile(trimmed_file)

    # Return the trimmed video file as a response
    return jsonify({'success': True, 'file': trimmed_file})

if __name__ == '__main__':
    app.run()
