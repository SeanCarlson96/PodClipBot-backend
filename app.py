from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from edit_video import edit_video

app = Flask(__name__)
CORS(app)

@app.route('/trim', methods=['POST'])
def trim_video():
    # Get the form data from the request
    video_file = request.files.get('video-file')
    start_time = float(request.form.get('start-time'))
    end_time = float(request.form.get('end-time'))

    # Save the edited video file to a specific directory, e.g., 'uploads'
    output_filename = edit_video(video_file, start_time, end_time)
    
    # Return the trimmed video file as a response
    return jsonify({'success': True, 'file': output_filename})

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    response = make_response(send_from_directory('uploads', filename))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'video/mp4'
    return response

if __name__ == '__main__':
    app.run()