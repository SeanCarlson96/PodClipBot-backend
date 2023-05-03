from flask import Flask, jsonify, request, send_from_directory, make_response, Response
from flask_cors import CORS
from auth_decorator import jwt_required
import time
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, get_jwt_identity
from models import User
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO
# from edit_video import edit_video
from edit_video_2 import edit_video_with_socketio, cancel_processing, clip_cancel_flags
import logging
from flask_mail import Mail, Message
import datetime

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
    def convert_to_seconds(timestamp):
        hours, minutes, seconds = map(int, timestamp.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    video_file = request.files.get('video-file')
    output_filenames = []

    # Save the video file to a temporary location to ensure readability
    temp_file = 'temp.mp4'
    video_file.save(temp_file)

    # Get all keys in the form data that start with 'start-time-'
    start_time_keys = [key for key in request.form.keys() if key.startswith('start-time-')]

    # Loop over the start time keys and extract the corresponding start and end times
    for index, start_time_key in enumerate(start_time_keys):
        clip_number = start_time_key.split('-')[-1]
        start_time = convert_to_seconds(request.form.get(start_time_key))
        end_time = convert_to_seconds(request.form.get(f'end-time-{clip_number}'))
        # output_filename = edit_video(temp_file, start_time, end_time, clip_number)
        output_filename = edit_video_with_socketio(temp_file, start_time, end_time, clip_number, socketio)
        output_filenames.append(output_filename)

    # Clear the clip_cancel_flags dictionary
    clip_cancel_flags.clear()

    return jsonify({'success': True, 'files': output_filenames})

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
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
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
    token = jwt.encode(
        {
            'user_id': str(user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        'your-secret-key',
        algorithm='HS256'
    )

    # Send a password reset email
    reset_url = f'http://your-frontend-url/reset-password?token={token}'
    msg = Message(
        'Password Reset Request',
        sender='noreply@example.com',
        recipients=[email]
    )
    msg.body = f'To reset your password, visit the following link: {reset_url}\n\nIf you did not request a password reset, please ignore this email.'
    mail.send(msg)

    return jsonify({"message": "Password reset email sent"}), 200

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Missing token or password"}), 400

    try:
        # Decode the token
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])

        # Check if the user exists in the database
        user = User.objects(id=payload['user_id']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the user's password

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.update(password_hash=hashed_password)

        return jsonify({"message": "Password reset successfully"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


if __name__ == '__main__':
    socketio.run(app)
