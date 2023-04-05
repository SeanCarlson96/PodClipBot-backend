from flask import Flask, jsonify, request, send_from_directory, make_response, Response
from flask_cors import CORS
from edit_video import edit_video
import time

app = Flask(__name__)
CORS(app)

@app.route('/trim', methods=['POST'])
def trim_video():
    video_file = request.files.get('video-file')
    start_time = float(request.form.get('start-time'))
    end_time = float(request.form.get('end-time'))
    output_filename = edit_video(video_file, start_time, end_time)
    return jsonify({'success': True, 'file': output_filename})


@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    response = make_response(send_from_directory('uploads', filename))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'video/mp4'
    return response


@app.route('/progress')
def progress():
    def generate():
        for i in range(101):
            yield 'data: %d\n\n' % i
            time.sleep(0.1)  # simulate delay
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run()