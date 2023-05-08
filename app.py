from flask import Flask, jsonify, request, send_file, send_from_directory, make_response, Response
from flask_cors import CORS
from auth_decorator import jwt_required
import time
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import decode_token, JWTManager, get_jwt_identity
from jwt.exceptions import PyJWTError
from jwt import decode
from models import User
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO
# from edit_video import edit_video
# from edit_video_2 import edit_video_with_socketio, cancel_processing, clip_cancel_flags
import logging
from flask_mail import Mail, Message
import datetime
from build_clip import build_clip, cancel_processing, clip_cancel_flags
from partial_content import partial_content_handler
from moviepy.editor import TextClip

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
app.config["MONGODB_SETTINGS"] = {
    'db': 'Cluster0',
    'host': os.environ["MONGODB_HOST"]
}
db = MongoEngine(app)
bcrypt = Bcrypt(app)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)

@socketio.on('cancel_processing')
def handle_cancel_processing(data):
    clip_name = data['clipName']
    print(f"Canceling clip {clip_name}")
    socketio.emit('video_processing_progress', {'progress': 0})
    cancel_processing(clip_name, socketio)

@app.route('/trim', methods=['POST'])
def trim_video():
    try:
        video_file = request.files.get('video-file')

        temp_file = 'temp.mp4'
        video_file.save(temp_file)        
        
        # Convert request.form into a regular dictionary, excluding start and end time data
        clip_info = {key: value for key, value in request.form.items() if not key.startswith(('start-time-', 'end-time-'))}


        music_file = request.files.get('music-file')
        if music_file:
            music_temp_file = 'temp_music.mp3'
            music_file.save(music_temp_file)
            clip_info['music_file_path'] = music_temp_file



        # Get all keys in the form data that start with 'start-time-'
        start_time_keys = [key for key in request.form.keys() if key.startswith('start-time-')]

        # Loop over the start time keys and extract the corresponding start and end times
        for index, start_time_key in enumerate(start_time_keys):
            clip_number = start_time_key.split('-')[-1]
            start_time = request.form.get(start_time_key)
            end_time = request.form.get(f'end-time-{clip_number}')

            build_clip(temp_file, start_time, end_time, clip_number, socketio, clip_info)

        clip_cancel_flags.clear()
        return jsonify({'success': True, 'message': '/trim completed all clips'})

    except Exception as e:
        # Return an error message to the front end
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# @app.route('/trim', methods=['POST'])
# def trim_video():
#     def convert_to_seconds(timestamp):
#         hours, minutes, seconds = map(int, timestamp.split(':'))
#         return hours * 3600 + minutes * 60 + seconds

#     video_file = request.files.get('video-file')
#     # output_filenames = []
#     print(request.form)

#     # Save the video file to a temporary location to ensure readability
#     temp_file = 'temp.mp4'
#     video_file.save(temp_file)

#     # Get all keys in the form data that start with 'start-time-'
#     start_time_keys = [key for key in request.form.keys() if key.startswith('start-time-')]

#     # Loop over the start time keys and extract the corresponding start and end times
#     for index, start_time_key in enumerate(start_time_keys):
#         clip_number = start_time_key.split('-')[-1]
#         start_time = convert_to_seconds(request.form.get(start_time_key))
#         end_time = convert_to_seconds(request.form.get(f'end-time-{clip_number}'))
#         # output_filename = edit_video(temp_file, start_time, end_time, clip_number)
#         # output_filename = edit_video_with_socketio(temp_file, start_time, end_time, clip_number, socketio)
#         edit_video_with_socketio(temp_file, start_time, end_time, clip_number, socketio)
#         # output_filenames.append(output_filename)

#     # Clear the clip_cancel_flags dictionary
#     clip_cancel_flags.clear()

#     return jsonify({'success': True, 'message': 'Clip construction completed'})

# @app.route('/uploads/<filename>', methods=['GET'])
# def serve_file(filename):
#     video_file_path = os.path.join('uploads', filename)
#     range_header = request.headers.get('Range', None)
    
#     if range_header:
#         return partial_content_handler(video_file_path, range_header)
#     else:
#         response = send_file(video_file_path, conditional=True)
#         response.headers['Content-Disposition'] = f'attachment; filename={filename}'
#         response.headers['Content-Type'] = 'video/mp4'
#         return response

# @app.route('/uploads/<filename>', methods=['GET'])
# def serve_file(filename):
#     response = make_response(send_from_directory('uploads', filename))
#     response.headers['Content-Disposition'] = f'attachment; filename={filename}'
#     response.headers['Content-Type'] = 'video/mp4'
#     return response

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    response = make_response(send_from_directory('uploads', filename))
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'video/mp4'
    response.headers['Cache-Control'] = 'no-store'  # Add this line
    return response

@app.route('/api/music_files', methods=['GET'])
def get_music_files():
    music_directory = 'music'
    music_files = os.listdir(music_directory)
    return jsonify(music_files)
@app.route('/api/music/<path:filename>', methods=['GET'])
def get_music_file(filename):
    return send_from_directory('music', filename)

@app.route('/progress')
def progress():
    def generate():
        for i in range(101):
            yield 'data: %d\n\n' % i
            time.sleep(0.1)  # simulate delay
    return Response(generate(), mimetype='text/event-stream')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    existing_user = User.objects(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email address already in use. Please use a different email address."}), 400

    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(email=data['email'], username=data['username'], password_hash=password_hash, subscription='none')
    user.save()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.objects.get(email=data['email'])
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        user_data = {
                        "id": str(user.id),
                        "email": user.email,
                        "username": user.username,
                        "subscription": user.subscription,
                    }
        return jsonify({"access_token": access_token, "user": user_data}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

@app.route('/protected', methods=['GET'])
@jwt_required
def protected_route():
    user_id = get_jwt_identity()
    user = User.objects.get(id=user_id)
    return jsonify({"message": f"Welcome, {user.username}!"})

# Configure Flask-Mail (use your own email settings)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'carlsonseanr@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
mail = Mail(app)

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    # Check if the email address already exists in the database
    user = User.objects(email=data['email']).first()
    if not user:
        return jsonify({"error": "Email not found"}), 404

    # Generate a reset token
    token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=1))

    # Send a password reset email
    reset_url = f'http://localhost:3000/reset-password?token={token}'
    msg = Message(
        'Password Reset Request',
        sender='noreply@example.com',
        recipients=[email]
    )
    msg.body = f'To reset your password, visit the following link: {reset_url}\n\nIf you did not request a password reset, please ignore this email.'
    # mail.send(msg) -- Commented out to prevent sending emails during development
    print(msg.body)

    return jsonify({"message": "Password reset email sent"}), 200

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or password"}), 400

    try:
        decoded_token = decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['sub']
        user = User.objects(id=user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the password
        password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        User.objects(id=user_id).update_one(set__password_hash=password_hash)


        return jsonify({"message": "Password updated successfully"}), 200

    except PyJWTError:
        return jsonify({"error": "Invalid or expired token"}), 401

@app.route('/api/fonts', methods=['GET'])
def get_fonts():
    fonts = TextClip.list('font')
    return jsonify(fonts)

if __name__ == '__main__':
    socketio.run(app)
